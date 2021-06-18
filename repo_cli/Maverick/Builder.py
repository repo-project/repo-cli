# -*- coding: utf-8 -*-
"""Builder

1. search source_dir recursively
2. build website structure
3. render pages
4. write to disk
"""

import os
import sys
import shutil
import functools
import pathlib

from .Utils import logged_func, print_color, Color, unify_joinpath, force_rmtree, run
from .Content import Content, ContentList
from .Config import Config
from . import Galileo


class TemplateError(BaseException):
    pass


class Builder:
    def __init__(self, conf: Config):
        self._config = conf
        self._posts = ContentList()
        self._pages = ContentList()

    @logged_func('')
    def clean(self):
        if os.path.exists(self._config.build_dir):
            try:
                shutil.rmtree(self._config.build_dir)
            except BaseException as e:
                print(e)

    @logged_func()
    def setup_theme(self):
        """Setup theme in this method.

        1. handle sys.path for local theme
        2. clone from remote for git theme
        3. install deps for theme
        """
        # template = ''
        # template_dep_file = ''
        # mvrk_path = self._config.mvrk_path

        # def clone_remote_theme(config: dict):
        #     repo_dir = os.path.abspath(mvrk_path + '/Templates/' + config['name'])
        #     if os.path.exists(repo_dir):
        #         force_rmtree(repo_dir)
        #
        #     repo_url = config['url']
        #     repo_branch = config.get('branch', 'master')
        #     repo_tag = config.get('tag', '')
        #
        #     def safe_run(command, cwd):
        #         try:
        #             run(command, cwd)
        #         except:
        #             raise TemplateError('Cannot fetch theme from '+repo_url)
        #
        #     safe_run('git clone -b %s %s %s' %
        #              (repo_branch, repo_url, repo_dir), mvrk_path)
        #     if repo_tag != '':
        #         safe_run('git checkout %s' & repo_tag, repo_dir)
        #
        # # 根据不同配置情况获取主题文件
        # if type(self._config.template) == str:
        #     # 如果主题配置项是一个字符串，则用户选用的是默认主题
        #     built_in_themes = ['Kepler', 'Galileo']
        #     if not os.path.exists(unify_joinpath(mvrk_path + '/Templates', self._config.template)):
        #         # 如果没有相应的主题文件
        #         if self._config.template in built_in_themes:
        #             # 如果主题是内置主题的一种，通过仓库获取主题
        #             clone_remote_theme({
        #                 "name": self._config.template,
        #                 "type": "git",
        #                 "url": "https://github.com/AlanDecode/Maverick-Theme-%s.git" % self._config.template,
        #                 "branch": "latest"
        #             })
        #             template = '.'.join(['Templates', self._config.template])
        #             template_dep_file = mvrk_path + '/Templates/%s/requirements.txt' % self._config.template
        #         else:
        #             # 否则，提示没有此主题
        #             raise TemplateError(
        #                 'Can not found local theme '+self._config.template)
        #     else:
        #         # TODO 如果是用户自己创建了一个同名文件
        #         # 如果存在响应的主题文件
        #         template = '.'.join(['Templates', self._config.template])
        #         template_dep_file = mvrk_path + '/Templates/%s/requirements.txt' % self._config.template
        #
        # elif type(self._config.template) == dict:
        #     # 如果主题配置项是一个字典，则根据配置获取主题文件
        #     if self._config.template['type'] == 'local':
        #         local_dir = os.path.abspath(self._config.template['path'])
        #         if not os.path.exists(local_dir):
        #             raise TemplateError(
        #                 'Can not found local theme '+self._config.template['name'])
        #         else:
        #             sys.path.insert(0, os.path.dirname(local_dir))
        #             template = self._config.template['name']
        #             template_dep_file = unify_joinpath(
        #                 local_dir, 'requirements.txt')
        #     elif self._config.template['type'] == 'git':
        #         clone_remote_theme(self._config.template)
        #         template = '.'.join(
        #             ['Templates', self._config.template['name']])
        #         template_dep_file = mvrk_path + '/Templates/%s/requirements.txt' % self._config.template['name']
        #
        # else:
        #     raise TemplateError('Invalid template config',
        #                         str(self._config.template))
        #
        # # handle deps for theme
        # if os.path.exists(template_dep_file) and os.path.isfile(template_dep_file):
        #     try:
        #         run('pip install -r %s' % template_dep_file, '.')
        #     except:
        #         raise TemplateError('Can not install dependencies for theme.')

        # 导入主题到运行环境
        self._template = Galileo

    def build_all(self):
        """Init building
        """

        # delete last build
        self.clean()

        print('Loading contents...')
        # test_src
        # os.walk
        # 生成目录树中的文件名，方式是按上->下或下->上顺序浏览目录树。
        # 对于以 top 为根的目录树中的每个目录（包括 top 本身）
        # 它都会生成一个三元组 (dirpath, dirnames, filenames)。
        # 按照层级关系从上往下迭代目录树，并且在每个层级都会生成三个元组 dirpath dirnames filenames
        # dirpath 存储当前目录层级的路径(相对还是绝对取决你你传入的是相对还是绝对
        # dirnames 存储当前层级存在的目录名
        # filenames 存储当前层级存在的文件名
        walker = os.walk(self._config.source_dir)
        # PurePath 一个通用的类，代表当前系统的路径风格
        source_abs_dir = pathlib.PurePath(
            os.path.abspath(self._config.source_dir))

        for path, _, filelist in walker:
            for file in filelist:
                # 如果是 md 文件
                if file.split(".")[-1].lower() == "md" or file.split(".")[-1].lower() == "markdown":
                        content_path = os.path.abspath(unify_joinpath(path, file))
                        content = Content(content_path)
                        if not content.get_meta("status").lower() in [
                                "publish", "published", "hide", "hidden"]:
                            continue

                        # 区分布局方案
                        layout = content.get_meta("layout").lower()
                        if layout == "post":
                            # 如果是通过文件布局分类，将文件布局情况解析出来并添加到文章源信息里
                            if (self._config.category_by_folder):
                                relative_path = pathlib.PurePath(
                                    content_path).relative_to(source_abs_dir)
                                relative_path = list(relative_path.parts[0:-1])
                                if len(relative_path) == 0:
                                    relative_path.append('Default')
                                content.update_meta(
                                    'categories', relative_path)
                            # 将解析好的文章导入到文章列表内
                            self._posts.append(content)
                        elif layout == "page":
                            # 将解析好的页面导入到页面列表内
                            content.update_meta('categories', [])
                            self._pages.append(content)

        print('Contents loaded.')
        # 通过制定方法重新排列文章顺序
        self._posts = ContentList(sorted(self._posts,
                                         key=functools.cmp_to_key(
                                             Content.cmp_by_date),
                                         reverse=True))
        self._pages = ContentList(sorted(self._pages,
                                         key=functools.cmp_to_key(
                                             Content.cmp_by_date),
                                         reverse=True))
        # 载入主题
        self.setup_theme()
        # 运行主题的解析函数
        self._template.render(self._config, self._posts, self._pages)

        print_color('\nAll done, enjoy.', Color.GREEN.value)
