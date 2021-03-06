from django import template
from loadgenomes.models import Tile, TileVariant

register = template.Library()

@register.filter
def avg_length(tile_var_list):
    if len(tile_var_list) > 0:
        return sum(tile_var.length for tile_var in tile_var_list)/float(len(tile_var_list))
    else:
        return None
@register.filter
def ref_avg_size(tile_var_list):
    length = sum(1 for tile_var in tile_var_list if tile_var.isReference())
    if length > 0:
        total_popul = sum(tile_var.population_size for tile_var in tile_var_list if tile_var.isReference())
        return total_popul/(2*float(length))
    else:
        return None

@register.filter
def ref_is_default(tile_list):
    return sum(1 for tile in tile_list if tile.defaultIsRef())

@register.filter
def ref_is_not_default(tile_list):
    return sum(1 for tile in tile_list if not tile.defaultIsRef())

@register.filter
def narrow_pos_to_chromosome(tile_list, chrom_int):
    chrom_int = int(chrom_int)-1
    if chrom_int < 0 or chrom_int > 26:
        assert False, "Incorrect chromosome integer format, expect an integer between 1 and 26"
    chr_path_lengths = [0,63,125,187,234,279,327,371,411,454,496,532,573,609,641,673,698,722,742,761,781,795,811,851,862,863]
    min_accepted = hex(chr_path_lengths[chrom_int])[2:]+"00"+"0000"
    min_accepted = int(min_accepted, 16)
    max_accepted = hex(chr_path_lengths[chrom_int+1])[2:]+"00"+"0000"
    max_accepted = int(max_accepted, 16)
    positions = Tile.objects.filter(tilename__gte=min_accepted).filter(tilename__lt=max_accepted)
    return positions
##    min_accepted = chr_path_lengths[chrom_int]
##    max_accepted = chr_path_lengths[chrom_int+1]
##    return [tile_var for tile_var in tile_var_list if tile_var.getPath() >= min_accepted and tile_var.getPath() < max_accepted]

@register.filter
def narrow_tiles_to_chromosome(tile_var_list, chrom_int):
    chrom_int = int(chrom_int)-1
    if chrom_int < 0 or chrom_int > 26:
        assert False, "Incorrect chromosome integer format, expect an integer between 1 and 26"
    chr_path_lengths = [0,63,125,187,234,279,327,371,411,454,496,532,573,609,641,673,698,722,742,761,781,795,811,851,862,863]
    min_accepted = hex(chr_path_lengths[chrom_int])[2:]+"00"+"0000" + "000"
    min_accepted = int(min_accepted, 16)
    max_accepted = hex(chr_path_lengths[chrom_int+1])[2:]+"00"+"0000"+"000"
    max_accepted = int(max_accepted, 16)
    tiles = TileVariant.objects.filter(tile_variant_name__gte=min_accepted).filter(tile_variant_name__lt=max_accepted)
    return tiles
