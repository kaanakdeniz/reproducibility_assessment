import re

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

encodings = {
    "link_c": "<LINK text='{0}'>",
    "link": "<LINK>",
    "code": "<CODE>",
    "image_c": "<IMAGE alt='{0}'>",
    "image": "<IMAGE>",
    "table_c": "<TABLE caption='{0}'>",
    "table": "<TABLE>",
    "cite": "<CITE>",
}


class ReadmeSectionParser:
    def __init__(self, repo, readme_html: str):
        self.repo = repo
        self.readme_html = readme_html
        self.soup = BeautifulSoup(self.readme_html, "html.parser")

    def mask_tag(self, tag, text=None):
        return encodings[tag] if text is None else encodings[f"{tag}_c"].format(text)

    def mask_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        for tag in soup.find_all("a"):
            text = re.sub(r'https?://\S+', '', tag.text).strip()
            tag.replaceWith(self.mask_tag("link") if text ==
                            "" else self.mask_tag("link", text))
        for tag in soup.find_all("img"):
            alt = None
            if tag.has_attr("alt"):
                alt = tag["alt"]
            mask = self.mask_tag("image") if alt is None else self.mask_tag(
                "image", alt)
            tag.replaceWith(mask)
        for tag in soup.find_all("pre"):
            if tag.text.startswith("@"):
                tag.replaceWith(self.mask_tag("cite"))
            else:
                tag.replaceWith(self.mask_tag("code"))
        for tag in soup.find_all("table"):
            caption = None
            if tag.has_attr("caption"):
                caption = tag["caption"]
            mask = self.mask_tag(
                "table") if caption is None else self.mask_tag("table", caption)
            tag.replaceWith(mask)
        # remain links:
        for link in soup.find_all(string=re.compile(r'https?://\S+')):
            link.replace_with(re.sub(r'https?://\S+', encodings["link"], link))

    def get_all_headings(self):
        headers = self.soup.find_all(re.compile("^h[1-6]$"))
        self.main_header = headers[0] if headers and headers[0].name == "h1" else None
        return headers

    def get_parent_header(self, heading):
        level = int(heading.name.removeprefix("h"))
        if level == 1 or heading == self.main_header:
            return None
        parent = heading.find_previous_sibling(
            re.compile(f"^h[1-{level - 1}]$"))
        if parent == self.main_header:
            return None
        return None if parent is None else parent.text.strip()

    def get_section_elements(self, heading, consider_level=False):
        p_tags = []
        elt = heading.nextSibling
        level = heading.name.removeprefix("h")
        regexp = f"^h{level}$" if consider_level else "^h[1-6]$"
        while elt is not None and not bool(re.search(regexp, str(elt.name))):
            text = elt.text.strip()
            if text != "":
                p_tags.append(text)
            elt = elt.nextSibling
        return p_tags

    @classmethod
    def merge_sections(cls, sections: pd.DataFrame, keys=None, with_newline=True) -> str:
        if keys is None:
            keys = ["header", "parent_header", "content"]
        separator = "\n" if with_newline else " "
        header_and_content = sections[keys].replace(np.nan, "").apply(
            lambda x: separator.join(filter(None, x)), axis=1)
        return separator.join(header_and_content) if with_newline else separator.join(header_and_content).replace("\n", " ")

    @classmethod
    def flatten_subheaders(cls, df, header, header_idx):
        subheaders = df.loc[header_idx:].loc[df['parent_header']
                                             == header, ['header']]
        flattened_subheaders = []
        if header in subheaders.header.values.tolist():
            flattened_subheaders.append(header)
            subheaders.drop(subheaders[subheaders['header'] == header].index,
                            inplace=True)
        for idx, subheader in subheaders.iterrows():
            flattened_subheaders.append(subheader.header)
            flattened_subheaders.extend(
                cls.flatten_subheaders(df, subheader.header, idx))
        return flattened_subheaders

    @classmethod
    def merge_contents(cls, df, header, header_idx):
        merged_content = df.loc[df['header'] ==
                                header, 'content'].values[0] + "\n"
        subheaders = cls.flatten_subheaders(df, header, header_idx)
        for subheader in subheaders:
            merged_content += subheader + "\n"
            merged_content += "\n".join(df.loc[df['header'] ==
                                               subheader, 'content'].values) + "\n"
        return merged_content

    @classmethod
    def group_by_parent_header(cls, df):
        df.loc[df.parent_header == "", "parent_header"] = np.nan
        base_headers = df[df["parent_header"].isna()].loc[:, :]
        return [{"repo": header.repo, "header": header.header, "content": cls.merge_contents(df, header.header, idx)} for idx, header in base_headers.iterrows()]

    def parse_sections(self, with_mask=True, group_by_parent=False):
        if with_mask:
            self.mask_soup(self.soup)
        sections = []
        headings = self.get_all_headings()
        for heading in headings:
            level = heading.name.removeprefix("h")
            parent = self.get_parent_header(heading)
            content = "\n".join(self.get_section_elements(heading))
            content = re.sub(r'\n+', '\n', content).strip()
            sections.append({
                "repo": self.repo,
                "level": level,
                "header": heading.text.strip(),
                "parent_header": parent,
                "content": content
            })
        if group_by_parent and sections:
            return self.group_by_parent_header(pd.DataFrame(sections))
        return sections
