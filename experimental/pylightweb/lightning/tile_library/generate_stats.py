from tile_library.models import Tile, TileVariant, TileLocusAnnotation, VarAnnotation, GenomeStatistic
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Count, Max, Min

from tile_library import functions
import time

def get_info(tiles, tilevars, silent=False):
    n = time.time()
    tile_info = tiles.annotate(num_variants=Count('variants')).aggregate(pos_num=Count('tilename'),
                                                                         avg_var_val=Avg('num_variants'),
                                                                         max_var_val=Max('num_variants')
                                                                         )
    x = time.time()
    if not silent:
        print "\tCount:", x-n
    tile_var_info = tilevars.aggregate(tile_num=Count('tile_variant_name'),
                                       min_len=Min('length'),
                                       avg_len=Avg('length'),
                                       max_len=Max('length')
                                       )
    y = time.time()
    if not silent:
        print "\tAggregation:", y-x
    #annotate_info = annotations.aggregate(max_tile_ann=Max(
    return tile_info, tile_var_info

def initialize(silent=False):
    impossible_name, impossible_varname = functions.get_min_position_and_tile_variant_from_chromosome_int(27)
    assert Tile.objects.filter(tilename__gte=impossible_name).exists() == False, "Invalid human genome: no tile id should exist with this path according to Tile.CHR_PATH_LENGTHS"
    assert TileVariant.objects.filter(tile_variant_name__gte=impossible_varname).exists() == False, "Invalid human genome: no tile_variant id should exist with this path according to Tile.CHR_PATH_LENGTHS"
    if GenomeStatistic.objects.count() == 0:
        for i in range(27):
            if i == 0:
                if not silent:
                    print "Entire Genome:"
                tile_info, tile_var_info = get_info(Tile.objects, TileVariant.objects, silent=silent)
            else:
                if not silent:
                    print "Chromosome", i, ":"
                min_pos, min_tile = functions.get_min_position_and_tile_variant_from_chromosome_int(i)
                max_pos, max_tile = functions.get_min_position_and_tile_variant_from_chromosome_int(i+1)
                max_pos -= 1
                max_tile -= 1
                tile_info, tile_var_info = get_info(Tile.objects.filter(tilename__range=(min_pos,max_pos)),
                                                    TileVariant.objects.filter(tile_variant_name__range=(min_tile, max_tile)), silent=silent)
            if not silent:
                print tile_info, tile_var_info
            s = GenomeStatistic(statistics_type=i, position_num=tile_info['pos_num'], tile_num=tile_var_info['tile_num'],
                                avg_variant_val=tile_info['avg_var_val'], max_variant_val=tile_info['max_var_val'],
                                min_length=tile_var_info['min_len'], avg_length=tile_var_info['avg_len'],
                                max_length=tile_var_info['max_len'])
            s.save()

    assert GenomeStatistic.objects.count() == 27, "Genome Statistics have already been generated. Run update()" 
    for path in range(Tile.CHR_PATH_LENGTHS[-1]):
        if not silent:
            print "Path", path
        min_path_pos, min_path_tile = functions.get_min_position_and_tile_variant_from_path_int(path)
        max_path_pos, max_path_tile = functions.get_min_position_and_tile_variant_from_path_int(path + 1)
        max_path_pos -= 1
        max_path_tile -= 1
        tile_info, tile_var_info = get_info(Tile.objects.filter(tilename__range=(min_path_pos,max_path_pos)),
                                            TileVariant.objects.filter(tile_variant_name__range=(min_path_tile, max_path_tile)), silent=silent)
        s = GenomeStatistic(statistics_type=27, path_name=path, position_num=tile_info['pos_num'], tile_num=tile_var_info['tile_num'],
                            avg_variant_val=tile_info['avg_var_val'], max_variant_val=tile_info['max_var_val'],
                            min_length=tile_var_info['min_len'], avg_length=tile_var_info['avg_len'],
                            max_length=tile_var_info['max_len'])
        s.save()
            
def update(path_only=False, silent=False):
    impossible_name, impossible_varname = functions.get_min_position_and_tile_variant_from_chromosome_int(27)
    assert Tile.objects.filter(tilename__gte=impossible_name).exists() == False, "Invalid human genome: no tile id should exist with this path according to Tile.CHR_PATH_LENGTHS"
    assert TileVariant.objects.filter(tile_variant_name__gte=impossible_varname).exists() == False, "Invalid human genome: no tile_variant id should exist with this path according to Tile.CHR_PATH_LENGTHS"
    try:
        if not path_only:
            for i in range(27):
                if i == 0:
                    if not silent:
                        print "Entire Genome:"
                    tile_info, tile_var_info = get_info(Tile.objects, TileVariant.objects, silent=silent)
                else:
                    if not silent:
                        print "Chromosome", i, ":"
                    min_pos, min_tile = functions.get_min_position_and_tile_variant_from_chromosome_int(i)
                    max_pos, max_tile = functions.get_min_position_and_tile_variant_from_chromosome_int(i+1)
                    max_pos -= 1
                    max_tile -= 1
                    tile_info, tile_var_info = get_info(Tile.objects.filter(tilename__range=(min_pos,max_pos)),
                                                        TileVariant.objects.filter(tile_variant_name__range=(min_tile, max_tile)), silent=silent)
                s = GenomeStatistic.objects.get(statistics_type=i)
                s.position_num = tile_info['pos_num']
                s.tile_num = tile_var_info['tile_num']
                s.min_length = tile_var_info['min_len']
                s.avg_length = tile_var_info['avg_len']
                s.max_length = tile_var_info['max_len']
                s.avg_variant_val = tile_info['avg_var_val']
                s.max_variant_val = tile_info['max_var_val']
                s.save()
        for path in range(Tile.CHR_PATH_LENGTHS[-1]):
            if not silent:
                print "Path", path
            min_path_pos, min_path_tile = functions.get_min_position_and_tile_variant_from_path_int(path)
            max_path_pos, max_path_tile = functions.get_min_position_and_tile_variant_from_path_int(path + 1)
            max_path_pos -= 1
            max_path_tile -= 1
            tile_info, tile_var_info = get_info(Tile.objects.filter(tilename__range=(min_path_pos,max_path_pos)),
                                                TileVariant.objects.filter(tile_variant_name__range=(min_path_tile, max_path_tile)), silent=silent)
            s = GenomeStatistic.objects.filter(statistics_type=27).get(path_name=path)
            s.position_num = tile_info['pos_num']
            s.tile_num = tile_var_info['tile_num']
            s.min_length = tile_var_info['min_len']
            s.avg_length = tile_var_info['avg_len']
            s.max_length = tile_var_info['max_len']
            s.avg_variant_val = tile_info['avg_var_val']
            s.max_variant_val = tile_info['max_var_val']
            s.save()
    except ObjectDoesNotExist:
        raise BaseException("tile_library.generate_stats.update() requires tile_library.generate_stats.initialize() to have run")
