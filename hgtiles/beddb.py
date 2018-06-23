import collections as col
import math
import sqlite3

def get_tileset_info(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    row = c.execute("SELECT * from tileset_info").fetchone();
    if row is not None and len(row) == 9:
        header = row[8]
    else:
        header = ""

    tileset_info = {
            'zoom_step': row[0],
            'max_length': row[1],
            'assembly': row[2],
            'chrom_names': row[3],
            'chrom_sizes': row[4],
            'tile_size': row[5],
            'max_zoom': row[6],
            'max_width': row[7],
            "min_pos": [1],
            "max_pos": [row[1]],
            "header": header
            }
    conn.close()

    return tileset_info

def tiles(filepath, tile_ids):
    '''
    Generate tiles from this dataset.

    Parameters
    ----------
    filepath: str
        The filename of the sqlite db file
    tile_ids: [str...]
        A list of tile ids of the form

    Returns
    -------
    tiles: [(tile_id, tile_value),...]
        A list of values indexed by the tile position
    '''
    to_return = []

    for  tile_id in tile_ids:
        parts = tile_id.split('.')
        uuid = parts[0]
        zoom = int(parts[1])
        xpos = int(parts[2])

        extra_zoom = 0
        new_rows = {}
        new_rows = []

        for j in range(2 ** extra_zoom):
            # the old rows are indexed by the higher
            # resolution tile numbers
            higher_xpos = 2 ** extra_zoom * xpos + j
            old_rows = get_1D_tiles(filepath, 
                    zoom + extra_zoom, 
                    higher_xpos)
            new_rows += old_rows
                
        print("new_rows length", len(new_rows))
        to_return += [(tile_id, new_rows)]

    return to_return

def get_1D_tiles(db_file, zoom, tile_x_pos, num_tiles=1):
    '''
    Retrieve a contiguous set of tiles from a db tile file.

    Parameters
    ----------
    db_file: str
        The filename of the sqlite db file
    zoom: int
        The zoom level
    tile_x_pos: int
        The position of the first tile
    num_tiles: int
        The number of tiles to retrieve

    Returns
    -------
    tiles: {pos: tile_value}
        A set of tiles, indexed by position
    '''
    tileset_info = get_tileset_info(db_file)
    conn = sqlite3.connect(db_file)

    c = conn.cursor()

    tile_width = tileset_info['max_width'] / 2 ** zoom

    tile_start_pos = tile_width * tile_x_pos
    tile_end_pos = tile_start_pos + num_tiles * tile_width

    query = '''
    SELECT startPos, endPos, chrOffset, importance, fields, uid
    FROM intervals,position_index
    WHERE
        intervals.id=position_index.id AND
        zoomLevel <= {} AND
        rEndPos >= {} AND
        rStartPos <= {}
    '''.format(zoom, tile_start_pos, tile_end_pos)

    rows = c.execute(query).fetchall()

    new_rows = []

    for r in rows:
        try:
            uid = r[5].decode('utf-8')
        except AttributeError:
            uid = r[5]

        tile_pos = (
            tile_x_pos + math.floor((r[0] - tile_start_pos) / tile_width)
        )

        x_start = r[0]
        x_end = r[1]

        for i in range(tile_x_pos, tile_x_pos + num_tiles):
            tile_x_start = i * tile_width
            tile_x_end = (i+1) * tile_width
            tile_pos = i

            if x_start < tile_x_end and x_end >= tile_x_start:
                new_rows += [
                    # add the position offset to the returned values
                    {'xStart': r[0],
                     'xEnd': r[1],
                     'chrOffset': r[2],
                     'importance': r[3],
                     'uid': uid,
                     'fields': r[4].split('\t')}]
    conn.close()

    return new_rows

def list_items(db_file, start, end, max_entries=None):
    '''
    List the entries between start and end

    Parameters
    ----------
    db_file: str
        The filename of the sqlite db file
    start_pos: int
        The start position from where to retrieve data
    end_pos: int
        The end position to get data
    max_entries: int
        The maximum number of results to return
    '''

    conn = sqlite3.connect(db_file)

    c = conn.cursor()

    # some large number because we want to extract all entries
    zoom = 100000

    query = '''
    SELECT startPos, endPos, chrOffset, importance, fields, uid
    FROM intervals,position_index
    WHERE
        intervals.id=position_index.id AND
        zoomLevel <= {} AND
        rEndPos >= {} AND
        rStartPos <= {}
    '''.format(zoom, start, end)

    if max_entries is not None:
        query += ' LIMIT {}'.format(max_entries)

    rows = c.execute(query).fetchall()

    new_rows = []

    for r in rows:
        try:
            uid = r[5].decode('utf-8')
        except AttributeError:
            uid = r[5]

        new_rows += [
            # add the position offset to the returned values
            {'xStart': r[0],
             'xEnd': r[1],
             'chrOffset': r[2],
             'importance': r[3],
             'uid': uid,
             'fields': r[4].split('\t')}]
    conn.close()

    return new_rows