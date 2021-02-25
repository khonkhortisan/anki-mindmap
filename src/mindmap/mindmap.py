from abc import ABC

from aqt import mw

from ._vendor.brain_dump.graphviz import create_mindmap_img
from .anki_util import get_notes, note_text
from .config import cfg
from .tree import tree, tree_to_markdown, without_leaves
from .util import redirect_stderr_to_stdout

NOTE_TEXT_LENGTH_LIMIT = 80


class Mindmap(ABC):

    def save_as_img(self, output_file_path, theme, include_notes):
        tree = self.tree if include_notes else without_leaves(self.tree)
        with redirect_stderr_to_stdout():
            create_mindmap_img(tree_to_markdown(tree), output_file_path, theme)

    def _paths(self):
        return [
            path
            for path in self.all_paths
            if self._has_matching_prefix(path)
        ]

    def _create_tree(self):
        result = self._tree_from_paths()
        result = self._add_note_texts_to_tree(result)
        return result

    def _tree_from_paths(self):
        result = tree()

        for path in self._paths():
            self._traverse_tree(result, path)

        return result

    def _add_note_texts_to_tree(self, a_tree):
        for path in self._paths():
            for note in get_notes(f'"{self.query}:{path}*"'):
                text = note_text(note, NOTE_TEXT_LENGTH_LIMIT)

                if text is None:
                    continue

                self._traverse_tree(a_tree, path)[text] = tree()
        return a_tree

    def _has_matching_prefix(self, path):
        prefix_parts = self.prefix.split(self.seperator)
        path_parts = path.split(self.seperator)
        for a, b in zip(prefix_parts, path_parts):
            if a != b:
                return False
        return True

    def _traverse(self, path):
        return self._traverse_tree(self, path)

    def _traverse_tree(self, tree, path):
        path_wh_prefix = self._without_prefix(path)
        parts = path_wh_prefix.split(self.seperator)
        cur = tree
        for p in parts:
            cur = cur[p]
        return cur

    def _without_prefix(self, name):
        prefix_depth = len(self.prefix.split(self.seperator))
        return self.seperator.join(name.split(self.seperator)[prefix_depth-1:])


class TagMindmap(Mindmap):

    def __init__(self, tag_prefix):
        self.prefix = tag_prefix
        self.all_paths = mw.col.tags.all()
        self.query = 'tag'
        self.seperator = cfg('tag_seperator')
        self.tree = self._create_tree()


class DeckMindmap(Mindmap):

    def __init__(self, deck_prefix):
        self.prefix = deck_prefix
        self.all_paths = mw.col.decks.allNames()
        self.query = 'deck'
        self.seperator = '::'
        self.tree = self._create_tree()