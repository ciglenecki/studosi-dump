import argparse
from collections import namedtuple
import glob
import json
import os
from pathlib import Path
import re
from typing import Dict, Iterable, List, Set

# region Named Tuples
Post = namedtuple("Post", ["author", "content", "votes", "reactions"])
Reactions = namedtuple("Reactions", ["haha", "wtf", "tuga"])
# endregion


# region Pathing
assets_folder = Path(__file__).resolve().parent / "assets"
discussions_json_folder = Path(__file__).resolve().parent / "discussions" / "json"
discussions_markdown_folder = (
    Path(__file__).resolve().parent / "discussions" / "markdown"
)
# endregion

# region Regex
WHITESPACE_REGEX = re.compile("\s+")
DIACRITIC_TO_ASCII = {
    "č": "c",
    "ć": "c",
    "đ": "dj",
    "š": "s",
    "ž": "z",
}
NONWORD_REGEX = re.compile(r"[\W\_]")
HEADING_REGEX = re.compile(r"^\#+")
ASSET_REGEX = re.compile(
    r"\!\[\]\((?P<path>assets\/\d{4}-\d{2}-\d{2}\/\d{5}\.[^\)]+)\)"
)
ASSET_FOLDER_REGEX = re.compile(r"\d{4}\-\d{2}\-\d{2}")
# endregion

# region Constants
PRIMARY_TAGS = [
    "FER",
    "Oglasi",
    "Opušteno",
    "Slubeno",
    "Studentska politika",
    "Sudnica",
]
SECONDARY_TAGS = [
    "Alati",
    "Informacije o predmetima",
    "Ispiti",
    "It's just a trolle bro",
    "Izlaganja",
    "Laboratorijske vježbe",
    "Na vlastitu odgovornost",
    "Organizacija",
    "Pikantno",
    "Pitalice",
    "Razgovor",
    "Vježba",
    "Zadaće",
]
LINES = "-" * 88
# endregion


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n_posts_per_page",
        "-n",
        type=int,
        default=10,
        help="Number of posts per page of Markdown. Default: 10",
    )

    return parser


# region Slugs
def tag_to_slug(tag: str):
    tag = str(tag).strip().lower()
    tag = WHITESPACE_REGEX.sub(" ", tag)
    tag = "".join(DIACRITIC_TO_ASCII.get(x, x) for x in tag)
    tag = NONWORD_REGEX.sub("-", tag)

    return tag


def tag_list_to_slug_list(
    tag_list: List[str],
    primary_tags: Iterable[str] = PRIMARY_TAGS,
    secondary_tags: Iterable[str] = SECONDARY_TAGS,
) -> List[str]:
    slug_span = [None, None]
    for i, tag in enumerate(tag_list):
        if tag in primary_tags:
            slug_span[0 if slug_span[0] is None else 1] = i
        if slug_span[1] is not None:
            break

    if slug_span[0] is None:
        return ["uncategorized"]
    elif slug_span[1] is None:
        slug_span[1] = len(tag_list)

    slug_list = list()
    for tag in tag_list[slug_span[0] : slug_span[1]]:
        if tag in secondary_tags:
            break

        slug = tag_to_slug(tag=tag)
        slug_list.append(slug)

    return slug_list


def get_discussion_slugs(discussion_dict):
    slug = discussion_dict["slug"]
    tags = discussion_dict["tags"]
    slug_list = tag_list_to_slug_list(tag_list=tags)

    return (*slug_list, slug)


# endregion

# region Post processing
def votes_dictionary_to_votes(votes: Dict[str, Iterable[str]]) -> int:
    plus = votes.get("upvoters", list())
    minus = votes.get("downvoters", list())

    plus = set(plus)
    minus = set(minus)
    minus = minus - plus

    return len(plus) - len(minus)


def reactions_dictionary_to_reactions(reactions: Dict[str, Iterable[str]]):
    haha = reactions.get("haha", list())
    wtf = reactions.get("wtf", list())
    tuga = reactions.get("tuga", list())

    haha = set(haha)
    wtf = set(wtf)
    tuga = set(tuga)

    wtf = wtf - haha
    tuga = tuga - wtf
    tuga = tuga - haha

    return Reactions(haha=len(haha), wtf=len(wtf), tuga=len(tuga))


def discussion_to_posts(discussion_dict) -> List[Post]:
    posts = discussion_dict["posts"]
    sorted_posts = [post for _, post in sorted(posts.items(), key=lambda x: int(x[0]))]
    normalized_posts = [
        Post(
            author=post["poster"],
            content=post["content"],
            votes=votes_dictionary_to_votes(post["votes"]),
            reactions=reactions_dictionary_to_reactions(post["reactions"]),
        )
        for post in sorted_posts
    ]

    return normalized_posts


def post_to_markdown(post: Post) -> str:
    content_lines = post.content.split("\n")
    content_lines = [HEADING_REGEX.sub("#\1", x) for x in content_lines]
    content = "\n".join(content_lines)

    return (
        f"# {post.author}:\n\n"
        f"{content}\n\n" + LINES + "\n\n"
        f"👍 {post.votes} 👎\n\n"
        f"😆: {post.reactions.haha} "
        f"😶: {post.reactions.wtf} "
        f"😢: {post.reactions.tuga}\n\n" + LINES
    )


def get_assets_from_content(content: str) -> Set[str]:
    return {str(match.group("path")).strip() for match in ASSET_REGEX.finditer(content)}


# endregion


def main():
    parser = get_parser()
    args = parser.parse_args()
    n = int(args.n_posts_per_page)
    assert n > 0, "Number of posts per page should be 1 or more"

    assets_directories = [assets_folder / name for name in os.listdir(assets_folder)]
    assets_directories = [
        x
        for x in assets_directories
        if os.path.isdir(str(x)) and ASSET_FOLDER_REGEX.fullmatch(x.name)
    ]
    assets_directories = assets_directories

    if len(assets_directories) == 0:
        raise RuntimeError(
            "No valid assets found. Ensure that dated folder (ex. 2022-07-01) is in "
            "the assets folder."
        )
    print(f"[INFO] Found {len(assets_directories)} assets subfolders")

    assets = list()
    for directory in assets_directories:
        assets.extend(glob.glob(str(directory / "*.*")))
    assets = set(assets)
    print(f"[INFO] Found {len(assets)} unique assets")

    discussion_jsons = glob.glob(str(discussions_json_folder / "*.json"))
    discussion_jsons = list(sorted(discussion_jsons))
    print(f"[INFO] Found {len(discussion_jsons)} discussions")

    for i, json_path in enumerate(discussion_jsons, 1):
        with open(json_path, mode="r", encoding="utf8", errors="replace") as f:
            json_dict = json.load(f)

        # Create posts destination path
        discussion_slugs = get_discussion_slugs(discussion_dict=json_dict)
        dest_folder = (
            discussions_markdown_folder
            / "/".join(discussion_slugs[:-1])
            / f"{discussion_slugs[-1]}"
        )

        # Process posts
        posts = discussion_to_posts(discussion_dict=json_dict)
        markdown = list()
        assets = set()
        for post in posts:
            markdown.append(post_to_markdown(post=post))
            assets.update(get_assets_from_content(content=post.content))

        # Create pages
        markdown_splits = [
            tuple(markdown[j : j + n]) for j in range(0, len(markdown), n)
        ]
        markdowns = ["\n\n".join(x) for x in markdown_splits]

        # Write pages
        os.makedirs(dest_folder, exist_ok=True)
        for j, m in enumerate(markdowns, 1):
            with open(
                dest_folder / f"page-{j:05}.md",
                mode="w+",
                encoding="utf8",
                errors="replace",
            ) as f:
                f.write(m)

        # Scan for assets
        assets = list(sorted(assets))
        assets_source_and_dest = [
            (assets_folder.parent / path, dest_folder / path) for path in assets
        ]

        # Create asset symbolic links
        for source, dest in assets_source_and_dest:
            if not os.path.exists(source):
                # Workaround for Windows
                os.makedirs(source.parent, exist_ok=True)
                with open(source, mode="w+", encoding="utf8", errors="replace") as f:
                    f.write("")
            os.makedirs(dest.parent, exist_ok=True)
            os.symlink(source, dest, target_is_directory=False)

        print(f"Progress: {i / len(discussion_jsons) * 100:.02f}%")


if __name__ == "__main__":
    main()
