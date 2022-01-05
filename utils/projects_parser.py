""" Contains parser for JetBrains IDEs "Recent projects" files """

import glob
import os
from collections import OrderedDict
from xml.etree import ElementTree

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from types.project import Project


# pylint: disable=too-few-public-methods
class ProjectsParser:
    """ Parser for JetBrains IDEs "Recent projects" files """

    @staticmethod
    def parse(file_path: str) -> list['Project']:
        """
        Parses the "Recent projects" file
        :param file_path: The path to the file
        :return: Parsed projects
        """

        if not os.path.isfile(file_path):
            return []

        root = ElementTree.parse(file_path).getroot()
        recent_projects_manager_path = './/component[@name="RecentProjectsManager"][1]'
        recent_directory_projects_manager_path = \
            './/component[@name="RecentDirectoryProjectsManager"][1]'

        raw_projects = \
            root.findall(
                f'{recent_projects_manager_path}/option[@name="recentPaths"]/list/option'
            ) + \
            root.findall(
                f'{recent_directory_projects_manager_path}/option[@name="recentPaths"]/list/option'
            ) + \
            root.findall(
                f'{recent_projects_manager_path}/option[@name="additionalInfo"]/map/entry'
            ) + \
            root.findall(
                f'{recent_directory_projects_manager_path}/option[@name="additionalInfo"]/map/entry'
            )
        project_paths = list(OrderedDict.fromkeys([
            (project.attrib['value' if 'value' in project.attrib else 'key']).replace(
                "$USER_HOME$", "~"
            ) for project in raw_projects
        ]))

        output = []
        for path in project_paths:
            name_file = path + '/.idea/.name'
            name = ''

            if os.path.exists(name_file):
                with open(name_file, 'r', encoding="utf8") as file:
                    name = file.read().replace('\n', '')

            icons = glob.glob(os.path.join(os.path.expanduser(path), '.idea', 'icon.*'))

            output.append({
                'name': name or os.path.basename(path),
                'path': path,
                'icon': icons[0] if len(icons) > 0 else None,
                'score': 0
            })

        return output
