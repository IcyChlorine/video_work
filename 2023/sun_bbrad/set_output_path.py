from manimlib import *
from manimhub import *

def set_output_path(file_writer):
	out_dir = file_writer.output_directory or ""
	scene_name = file_writer.file_name or file_writer.get_default_scene_name()

	if not file_writer.write_to_movie: 
		return
	
	movie_dir = guarantee_existence(os.path.join(out_dir, "footage"))
	movie_file = add_extension_if_not_present(scene_name, file_writer.movie_file_extension)
	file_writer.movie_file_path = os.path.join(movie_dir, movie_file)

	if not file_writer.break_into_partial_movies:
		return
    
	file_writer.partial_movie_directory = guarantee_existence( \
		os.path.join(movie_dir, scene_name,))