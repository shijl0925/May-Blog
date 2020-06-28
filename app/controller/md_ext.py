#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author: Jialiang Shi
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class BootstrapTreeprocessor(Treeprocessor):
    def run(self, node):
        for child in node.getiterator():
            if child.tag == 'table':
                child.set("class", "table table-bordered")
        return node


class BootStrapExtension(Extension):
    def __init__(self, configs):
        self.config = configs
        super(BootStrapExtension, self).__init__()

    def extendMarkdown(self, md):
        md.registerExtension(self)

        bootstrap_tree_processor = BootstrapTreeprocessor()
        md.treeprocessors.add('bootstraptreeprocessor', bootstrap_tree_processor, '_end')

