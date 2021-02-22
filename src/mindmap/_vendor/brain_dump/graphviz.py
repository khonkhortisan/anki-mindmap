import locale
from ..pydot import pydot

from .parsers.indented_text_graph import parse as parse_text_graph


class Theme:
    SOLARIZED_BG_COLOR = '#012b37'

    BRIGHT_EDGE_COLORS = [ # Pallette from https://flatuicolors.com/palette/defo
        '#f1c40f',
        '#e67e22',
        '#8e44ad',
        '#e74c3c',
        '#2980b9',
        '#c0392b',
        '#1abc9c',
        '#27ae60',
        '#95a5a6',
    ]

    SOLARIZED_EDGE_COLORS = [  # Palette from http://ethanschoonover.com/solarized
        '#b58900',
        '#cb4b16',
        '#6c71c4',
        '#dc323f',
        '#268bd2',
        '#d33682',
        '#2aa198',
        '#859900',
        '#939393',
    ]

    def __init__(self, bg_color, label_color, edge_colors):
        self.graph_style = dict(
            layout='twopi',
            overlap='false',
            splines='curved',
            fontname='arial',
            bgcolor=bg_color,
            outputorder="edgesfirst",
        )
        self.label_color = label_color
        self.edge_colors = edge_colors

    def edge_style(self, dest_node, graph_height):
        color = self.edge_colors[dest_node.branch_id % len(self.edge_colors)]
        return dict(
            color=color,
            dir='none',
            penwidth=2 * (2 + graph_height - dest_node.depth),
        )

    def node_style(self, node, graph_height):
        label = node.content.strip(
        ) if node.content and node.content != node.ROOT_DEFAULT_NAME else ''
        return dict(
            group=node.branch_id,
            shape='plaintext',
            label=label,
            fontcolor=self.label_color,
            fontsize=2 * (16 + graph_height - node.depth),
            fontname=self.graph_style['fontname'],  # not inherited by default
        )

    @classmethod
    def darksolarized(cls):
        return cls(cls.SOLARIZED_BG_COLOR, 'white', cls.SOLARIZED_EDGE_COLORS)

    @classmethod
    def bright(cls):
        return cls('white', 'black', cls.BRIGHT_EDGE_COLORS)


def create_solarized_mindmap_img(input_filepath, output_file_path, theme=Theme.bright(), root_label=None):
    # needed to print 'Duplicate content' warning without error and to bypass pydot Dot.write default raw formatting on line 1769
    assert locale.getdefaultlocale()[1] == 'UTF-8'
    with open(input_filepath) as txt_file:
        text = txt_file.read()
    graph = parse_text_graph(text, root_label=root_label)
    create_mindmap(graph, output_file_path, theme=theme)


def create_mindmap(graph, output_svg_path, theme):
    graph_height = graph.height
    pygraph = pydot.Dot(root=graph.content, **theme.graph_style)
    for node in graph:
        # avoid erroneous pydot 'port' detection + workaround this: https://github.com/erocarrera/pydot/issues/187
        content = pydot.quote_if_necessary(node.content)
        pygraph.add_node(pydot.Node(
            content, **theme.node_style(node, graph_height)))
        if node.parent:
            parent_content = node.parent.content if ':' not in node.parent.content else '"{}"'.format(
                node.parent.content)
            pygraph.add_edge(pydot.Edge(parent_content, content,
                                        **theme.edge_style(node, graph_height)))
    pygraph.write_svg(output_svg_path, prog='twopi')
