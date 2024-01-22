#!/usr/bin/env python3

import re
import sys

from lxml import etree


def get_text(el):
    s = el.text or ""
    for child in el:
        s += get_text(child)
    s += el.tail or ""
    s = re.sub(r"\s+", " ", s)
    return s


def labeller(el):
    if "type" in el.attrib:
        return el.tag + "_" + el.attrib["type"]
    elif "class" in el.attrib:
        return el.tag + "_" + el.attrib["class"]
    elif "rend" in el.attrib:
        return el.tag + "_" + el.attrib["rend"]
    else:
        return el.tag


def flatten_element(element, path, ref_prefix, config):
    if element.tag in config["block"]:
        children = [el for el in element if el.tag not in config["ignore"]]
        num_children = len(children)
        ref = 0
        for idx, child in enumerate(children, 1):
            if idx == 1:
                if idx == num_children:
                    path_addition = [labeller(element) + ":only"]
                else:
                    path_addition = [labeller(element) + ":first"]
            elif idx == num_children:
                path_addition = [labeller(element) + ":last"]
            else:
                path_addition = [labeller(element) + ":inside"]
            if child.tag == "header":
                if child.attrib.get("type") == "subtitle":
                    ref_string = (ref_prefix + "." if ref_prefix else "") + "subhead"
                else:
                    ref_string = (ref_prefix + "." if ref_prefix else "") + "header"
            else:
                ref += 1
                ref_string = (ref_prefix + "." if ref_prefix else "") + f"{ref:03d}"
            flatten_element(child, path + path_addition, ref_string, config)
    elif element.tag in config["block-with-inline"]:
        print(
            ref_prefix,
            "{" + labeller(element) + "}",
            # " ".join(path),
            get_text(element).strip(),
            sep="\t",
        )
    elif element.tag in config["ignore"]:
        pass
    else:
        print("Unknown element: {}".format(element.tag), file=sys.stderr)
        sys.exit(1)


def flatten_xml(filename, ref_prefix, config):
    tree = etree.parse(filename)
    root = tree.getroot()

    flatten_element(root, [], ref_prefix, config)


if __name__ == "__main__":
    CONFIG = {
        "block": ["text", "div", "lg"],
        "block-with-inline": ["header", "p", "l"],
        "ignore": [],
    }

    flatten_xml("na_markup.xml", None, CONFIG)
