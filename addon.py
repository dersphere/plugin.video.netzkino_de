#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2012 Tristan Fischer (sphere@dersphere.de)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from xbmcswift2 import Plugin
from resources.lib.api import NetzkinoApi, NetworkError

plugin = Plugin()
api = NetzkinoApi()


@plugin.route('/')
def show_categories():
    categories = api.get_categories()
    items = [{
        'label': item['title'],
        'path': plugin.url_for(
            endpoint='show_movies',
            category_id=str(item['id'])
        )
    } for item in categories]
    return plugin.finish(items)


@plugin.route('/category/<category_id>')
def show_movies(category_id):
    @plugin.cached()
    def get_movies(category_id):
        category_items = api.get_movies(category_id)
        items = [{
            'label': item['title'],
            'thumbnail': item['image'],
            'info': {
                'plot': item['content'] or '',
            },
            'path': plugin.url_for(
                endpoint='play_movie',
                stream_path=item['stream_path']
            ),
            'is_playable': True
        } for item in category_items]
        return items

    plugin.set_content('movies')
    items = get_movies(category_id)
    finish_kwargs = {}
    if plugin.get_setting('force_viewmode') == 'true':
        finish_kwargs['view_mode'] = 'thumbnail'
    return plugin.finish(items, **finish_kwargs)


@plugin.route('/movie/<stream_path>/')
def play_movie(stream_path):
    stream_func = plugin.get_setting('playback_mode', choices=(
        api.get_mp4_url,
        api.get_rtmp_url,
        api.get_hls_url
    ))
    stream_url = stream_func(stream_path)
    return plugin.set_resolved_url(stream_url)

if __name__ == '__main__':
    try:
        plugin.run()
    except NetworkError:
        plugin.log.error(NetworkError)
        plugin.notify(msg=plugin.get_string('30200'))
