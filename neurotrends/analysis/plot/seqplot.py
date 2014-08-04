"""

"""

import matplotlib.pyplot as plt
import seaborn as sns

PALETTE_NAME = 'Set3'
SIZE_SCALE = 5000
ZORDER_OFFSET = 999999

def multi_rank_plot(ranks_combined, group_labels, rank_groups, outname=None):

    plt.figure()

    palette = sns.utils.color_palette(PALETTE_NAME, len(ranks_combined))
    rects = []

    sorted_indices = sorted(
        range(len(ranks_combined)),
        key=lambda idx: ranks_combined[idx]['avg'],
    )

    # Draw scatters
    for gidx, rank_group in enumerate(rank_groups):

        for pos, idx in enumerate(sorted_indices):
            rank = rank_group[idx]
            plt.scatter(
                rank['avg'], gidx,
                s=rank['prop'] * SIZE_SCALE,
                zorder=1 / rank['prop'],
                color=palette[pos],
            )

    for idx in range(len(sorted_indices)):
        rects.append(
            plt.Rectangle(
                (0, 0), 1, 1,
                color=palette[idx],
            )
        )

    # Set up axes
    ax = plt.gca()

    ax.set_xlabel('Normalized Rank Order')
    ax.set_ylabel('Analysis Package')

    plt.yticks(
        range(len(group_labels)),
        group_labels
    )

    ax.invert_yaxis()

    # Draw legend
    lgd = plt.legend(
        rects,
        [ranks_combined[idx]['label'] for idx in sorted_indices],
        loc='upper left', bbox_to_anchor=(1, 1),
    )
    lgd.get_frame().set_facecolor('none')

    # Optionally save
    if outname:
        plt.savefig(
            outname + '.pdf',
            bbox_extra_artists=(lgd,),
            bbox_inches='tight',
        )


def rank_plot(ranks, outname=None):

    plt.figure()

    palette = sns.utils.color_palette(PALETTE_NAME, len(ranks))
    rects = []

    sorted_ranks = sorted(ranks, key=lambda rank: rank['avg'])

    # Draw scatters
    for idx, rank in enumerate(sorted_ranks):
        plt.scatter(
            rank['avg'], 0,
            s=rank['prop'] * SIZE_SCALE,
            zorder=1 / rank['prop'],
            color=palette[idx],
        )
        rects.append(
            plt.Rectangle(
                (0, 0), 1, 1,
                color=palette[idx],
            )
        )

    # Set up axes
    ax = plt.gca()

    ax.set_xlabel('Normalized Rank Order')
    ax.set_yticks([])

    # Draw legend
    lgd = plt.legend(
        rects,
        [rank['label'] for rank in sorted_ranks],
        loc='upper left', bbox_to_anchor=(1, 1),
    )
    lgd.get_frame().set_facecolor('none')

    # Optionally save
    if outname:
        plt.savefig(
            outname + '.pdf',
            bbox_extra_artists=(lgd,),
            bbox_inches='tight',
        )
