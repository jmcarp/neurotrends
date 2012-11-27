# Requires ggplot2_0.9.1, ggmap_2.1
# May require downgrade from current packages

# Import libraries
library(fastcluster)    # Speed up built-in clustering tools
library(geosphere)      # Centroids and other geographic functions
library(ggmap)          # Map package for ggplot2
library(Hmisc)
library(gridExtra)
library(png)

# Directories
tmpdir = '/tmp'

#######################
## Utility functions ##
#######################

# Extract legend from grob
# Modified from https://github.com/hadley/ggplot2/wiki/Share-a-legend-between-two-ggplot2-graphs
g_legend = function(a.gplot) {
  tmp = ggplot_gtable(ggplot_build(a.gplot))
  leg = which(sapply(tmp$grobs, function(x) x$name) == 'guide-box')
  legend = tmp$grobs[[leg]]
  return(legend)
}

# Great-circle distance matrix (modified from fields::rdist.earth)
# ifselse() replaced with vector indexing for speed
rdist.earth.mod = function (x1, x2, miles = TRUE, R = NULL)
{
    if (is.null(R)) {
        if (miles)
            R <- 3963.34
        else R <- 6378.388
    }
    coslat1 <- cos((x1[, 2] * pi)/180)
    sinlat1 <- sin((x1[, 2] * pi)/180)
    coslon1 <- cos((x1[, 1] * pi)/180)
    sinlon1 <- sin((x1[, 1] * pi)/180)
    if (missing(x2)) {
        pp <- cbind(coslat1 * coslon1, coslat1 * sinlon1, sinlat1) %*%
            t(cbind(coslat1 * coslon1, coslat1 * sinlon1, sinlat1))
        gtone = abs(pp) > 1
        pp[gtone] = sign(pp[gtone])
        pp[!gtone] = pp[!gtone]
        return(R * acos(pp))
    }
    else {
        coslat2 <- cos((x2[, 2] * pi)/180)
        sinlat2 <- sin((x2[, 2] * pi)/180)
        coslon2 <- cos((x2[, 1] * pi)/180)
        sinlon2 <- sin((x2[, 1] * pi)/180)
        pp <- cbind(coslat1 * coslon1, coslat1 * sinlon1, sinlat1) %*%
            t(cbind(coslat2 * coslon2, coslat2 * sinlon2, sinlat2))
        gtone = abs(pp) > 1
        pp[gtone] = sign(pp[gtone])
        pp[!gtone] = pp[!gtone]
        return(R * acos(pp))
    }
}

# Geographic mean (modified from geosphere::geomean)
geomean.mod = function (xy, w = NULL)
{
    if (inherits(xy, "SpatialPolygons") | inherits(xy, "SpatialPoints")) {
        stopifnot(isLonLat(xy))
        xy <- coordinates(xy)
    }
    xy <- na.omit(xy)
    xy[, 1] <- xy[, 1] + 180
    xy <- xy * pi/180
    if (is.null(w)) {
        w <- 1
    }
    else if (length(w) != nrow(xy)) {
        stop("length of weights not correct. It should be: ",
            nrow(xy))
    }
  w <- w/sum(w)
    Sx <- mean(sin(xy[, 1]) * w)
    Cx <- mean(cos(xy[, 1]) * w)
    x <- atan2(Sx, Cx)
    x <- x%%(2 * pi) - pi
    Sy <- mean(sin(xy[, 2]) * w)
    Cy <- mean(cos(xy[, 2]) * w)
    y <- atan2(Sy, Cy)
    cbind(x, y) * 180/pi
}

# Get gmap bounding box
gmap.bbox = function(gmap) {
	
	# Initialize
	bbox = c()
	
	# Get span
	bbox$lonspn = gmap$data$lon[c(1,2)]
	bbox$latspn = gmap$data$lat[c(1,3)]
	
	# Get range
	bbox$lonrng = diff(bbox$lonspn)
	bbox$latrng = diff(bbox$latspn)
	
	# Return
	bbox
	
}

# Generate ggplot-style color palette
# From http://stackoverflow.com/questions/8197559/emulate-ggplot2-default-color-palette
ggplotColours = function(n=6, h=c(0, 360) + 15) {
	if ((diff(h) %% 360) < 1) {
		h[2] = h[2] - 360 / n
	}
	hcl(h=seq(h[1], h[2], length=n), c=100, l=65)
}

#
group.coords = function(data, k=NULL, h=NULL, minnum=50) {

	# Get geo distance matrix
  distdata = data[c('lon', 'lat')]
  if (dim(distdata)[1] > minnum) {
    distdata = unique(distdata)
  }
  dist = rdist.earth.mod(distdata)
	
	if (k == 1) {

		# One cluster: do nothing
		groups = rep(1, length(data$lon))

	} else {

		# Multiple clusters: Run hclust()
		tree = hclust(as.dist(dist), method='ward')

    if (dim(data)[1] > minnum) {

      unique.groups = cutree(tree, k, h)
      groups = rep(0, dim(data)[1])
      for (groupidx in 1 : length(unique.groups)) {
        group.coord = distdata[groupidx,]
        orig.idx = data$lon == group.coord$lon & 
          data$lat == group.coord$lat
        groups[orig.idx] = unique.groups[groupidx]
      }

    } else {

      groups = cutree(tree, k, h)

    }
	}
	
  # 
	cens = c()

	for (groupidx in 1 : max(groups)) {

		groupdata = data[groups==groupidx,]
		geodata = groupdata[c('lon', 'lat')]
		# Number of unique coordinates
		ucoord = length(unique(geodata))
		# Number of unique longitudes
		ulon = length(unique(groupdata$lon))
		# Number of unique latitudes
		ulat = length(unique(groupdata$lat))
		if (ucoord < 3 | ulon == 1 | ulat == 1) {
			cen = geomean.mod(geodata)
		} else {
			cen = centroid(cbind(groupdata$lon, groupdata$lat))
		}
		cens = rbind(cens, cen)
	}
	
	list(groups=groups, cens=cens)
	
}

########################
## Plotting functions ##
########################

# Default options for pie grobs
pie.opts = opts(
	panel.background=theme_rect(fill='transparent', colour=NA),
	plot.background=theme_rect(fill='transparent', colour=NA),
	panel.grid.minor=theme_blank(),
	panel.grid.major=theme_blank(),
	axis.ticks=theme_blank(),
	axis.text.x=theme_blank(),
	axis.text.y=theme_blank(),
	panel.border=theme_blank(),
  legend.position='none'
)

# Get pie chart grob
pie.grob = function(data, colname, edgecol='transparent', 
    wedgecols=NULL, method='indirect', dpi=100) {

  # Set fill column
	data$fill = factor(data[,colname])

  # Make plot
	plotobj = ggplot(data, aes(x='', fill=fill)) +
		geom_bar(width=1, colour=edgecol) +
    coord_polar(theta='y') + 
    labs(x='', y='') +
    pie.opts

  # Specify colors
	if (!is.null(wedgecols)) {
		plotobj = plotobj + scale_fill_manual(values=wedgecols)
	}

  if (method == 'direct') {
    
    # Build grob from ggplot object
    grob = ggplotGrob(plotobj)

  } else if (method == 'indirect') {

    # Get PNG name
    pngname = sprintf('%s/grob.png', tmpdir)

    # Save pie chart to PNG
    # Set height and width to defaults to avoid output
    ggsave(plotobj, filename=pngname, dpi=dpi, bg='transparent',
      height=7, width=7)

    # Read PNG
    pieimg = readPNG(pngname)

    # Build grob from PNG
    grob = rasterGrob(pieimg)

    # Delete PNG
    unlink(pngname)

  }

  # Return grob
	grob

}

# 
piemap = function(gmap, cgrob, cx, cy, cd, 
    offset=FALSE, addpoints=FALSE) {
	
	# Get offsets
	bbox = gmap.bbox(gmap)
  if (offset) {
    xoff = -0.0195 * bbox$lonrng
    yoff = -0.0195 * bbox$latrng
  } else {
    xoff = 0
    yoff = 0
  }
	
	# Initialize gmap
	ggobj = gmap + 
		opts(legend.position='none')

	# Add pie grobs in ascending size order
	for (gidx in order(cd)) {
		
    # Skip empty grobs
    if (typeof(cgrob[[gidx]]) == 'logical') {
      next
    }
    
    # Get x-coordinates
    xmin = cx[gidx] - (cd[gidx] * bbox$lonrng) + xoff
    xmax = cx[gidx] + (cd[gidx] * bbox$lonrng) + xoff

		# Hack: Center vertically in Mercator coordinates
		ycen.geo = cy[gidx]
		ybot.geo = cy[gidx] - (cd[gidx] * bbox$latrng) * 1.25
		ycen.xy = mercator(c(0, ycen.geo))[2]
		ybot.xy = mercator(c(0, ybot.geo))[2]
		ytop.xy = ycen.xy + (ycen.xy - ybot.xy)
		ytop.geo = mercator(c(0, ytop.xy), inverse=TRUE)[2]

    # Get y-coordinates
    ymin = ybot.geo + yoff
    ymax = ytop.geo + yoff
		
		# Add pie grob
		ggobj = ggobj + inset(
			cgrob[[gidx]], 
			xmin = xmin,
			xmax = xmax,
			ymin = ymin,
			ymax = ymax
		)
		
	}
	
	# Add points
	if (addpoints) {
		ggobj = ggobj +
			geom_point(aes(x=cx, y=cy, size=3), data=data.frame(cx=cx, cy=cy))
	}
	
	ggobj
	
}

#
plot.groups = function(data, gmap, dv='pkg', k=NULL, h=NULL, 
    title='', maxsize=NULL, scale=NULL, splitvar=NULL, outname=NULL) {
	
	# Trim out-of-range points
	bbox = gmap.bbox(gmap)
	incidx = data$lon >= bbox$lonspn[1] & data$lon <= bbox$lonspn[2] &
		data$lat >= bbox$latspn[1] & data$lat <= bbox$latspn[2]
	incdata = data[incidx,]
	
	# Re-order factor by frequency
	incdata[,dv] = factor(incdata[,dv])
	dvtab = table(incdata[,dv])
	dvlev = names(sort(dvtab, decreasing=TRUE))

  # Move other to end
  if ('other' %in% dvlev) {
    dvlev = dvlev[dvlev != 'other']
    dvlev = c(dvlev, 'other')
  }

	incdata[,dv] = factor(incdata[,dv], levels=dvlev)
	nlev = length(dvlev)
	
	# Get color palette
	cols = ggplotColours(nlev)
	
	# Get geo centroids
	groupinfo = group.coords(incdata, k, h)
	groups = groupinfo$groups
	cens = groupinfo$cens
	ngroup = max(groups)
	
  # Get split variable
  if (is.null(splitvar)) {
    incdata$splittmp = 'All'
    splitvar = 'splittmp'
  }
  
  # Get values of split variable
  usplit = unique(incdata[,splitvar])
  usplit = sort(usplit)

  # Initialize count variables
  counts = list()
  maxcount = 0
  
  # Get grob counts
  for (splitidx in 1 : length(usplit)) {

    # Get value of split variable
    splitval = usplit[splitidx]

    # Initialize sizes for split variable
    splitcounts = c()
    
    # Get row indices for split variable
    splitpos = incdata[,splitvar] == splitval

    # Get counts
    for (groupidx in 1 : max(groups)) {
      splitcount = sum(groups[splitpos] == groupidx)
      splitcounts = c(splitcounts, splitcount)
      maxcount = max(maxcount, splitcount)
    }

    # Append to size list
    counts[[splitidx]] = splitcounts

  }

  # Set up graphics
  graphics.off()
  dev.new()
  defdev = dev.cur()

  # Set up PDF
  if (!is.null(outname)) {
    pdf(outname)
    dev.set(defdev)
  }

  for (splitidx in 1 : length(usplit)) {
    
    # Get value of split variable
    splitval = usplit[splitidx]

    # Initialize
    groblist = list()
    splitpos = incdata[,splitvar] == splitval
    
    # Make pie grobs
    for (groupidx in 1 : max(groups)) {
      
      # Get data for geo group
      groupdata = incdata[splitpos & groups == groupidx,]
      
      # Get colors
      grobcols = cols[table(groupdata[,dv]) > 0]
      
      # Add pie grob
      if (dim(groupdata)[1] > 0) {
        groblist = append(groblist, 
          list(pie.grob(groupdata, dv, wedgecols=grobcols)))
      } else {
        groblist = append(groblist, FALSE)
      }
      
    }
    
    # Scale counts
    if (!is.null(maxsize)) {
      counts[[splitidx]] = counts[[splitidx]] / maxcount * maxsize
    } else if (!is.null(scale)) {
      counts[[splitidx]] = counts[[splitidx]] * scale
    }

    # Get sizes
    sizes = sqrt(counts[[splitidx]] / pi)
    
    # Add pie grobs to map
    mapobj = piemap(gmap, groblist, cens[,1], cens[,2], sizes)

    # Add title
    mapobj = mapobj + opts(title=sprintf('%s: %s', title, splitval))

    # Hack: Add legend
    legcoord = rep(0, length(dvlev))
    legdf = data.frame(fill=factor(dvlev, levels=dvlev), 
      lon=legcoord, lat=legcoord)
    legmap = gmap + 
      geom_polygon(aes(x=lon, y=lat, fill=fill), data=legdf) +
      scale_fill_manual(values=cols) + 
      guides(fill=guide_legend(title=NULL))
    legobj = g_legend(legmap)

    # Combine map and legend
    grid.arrange(mapobj + opts(legend.position='none'), legobj,
      widths=unit.c(unit(1, 'npc') - legobj$width, legobj$width), 
      ncol=2)
    
    # Copy figure to PDF
    if (!is.null(outname)) {
      dev.copy()
      dev.set(defdev)
    }

  }

  # Close PDF device
  if (!is.null(outname)) {
    dev.off(defdev + 1)
  }

}
