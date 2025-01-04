###############################################################################
# SIMPLE C TEMPLATE GENERATOR                                                 #
# Creates a basic C skeleton with boilerplate and headers                     #
###############################################################################
from sys import argv
from datetime import datetime
from os import getcwd, mkdir
import argparse

COMMENT_BLOCK_COLUMN_SIZE           = 80
COMMENT_BLOCK_PRE_TEXT_BLANK_LINES  = 1
COMMENT_BLOCK_POST_TEXT_BLANK_LINES = 1

UTILITY_HEADER = "utils"
UTILITY_SOURCE = "utils"

'''
Utility code
'''

utility_header = """
#pragma once

#include <stdint.h>
#include <stdbool.h>

typedef struct _map
{
     int       map_fd;
     size_t    map_size;
     uint8_t*  map_ptr;
     bool      mapped;
}Map, *PMap;


void hexdump( const uint8_t* buffer, const size_t size );
bool map_file( const char* filename, PMap m );
bool unmap_file( PMap m );
"""


utility_code = """
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <elf.h>

#include "utils.h"

void hexdump( const uint8_t* buffer, const size_t size )
{
    size_t i = 0, j = 0;

    for( i = 0; i < size; i += 16 )
    {
    	printf( "0x%08lX: ", i );
    	for( j = 0; j < 16; j++ )
    	{
    		if( (i+j) < size )
    		{
    			printf( "%02X ", buffer[i+j] );
    		}
    		else
    		{
    			printf( "   " );
    		}
    	}
    	printf( "		" );
    	for( j = 0; j < 16; j++ )
    	{
    		if( (i+j) < size )
    		{
    			uint8_t temp = buffer[i+j];
    			if( temp >= 0x20 && temp < 0x7F )
    			{
    				printf( "%c", temp );
    			}
    			else
    			{
    				printf( "." );
    			}
    		}
    		else
    		{
    			printf( " " );
    		}
    	}
    	printf( "\\n" );
    }
}

bool map_file( const char* filename, PMap m )
{
     int      temp_fd  = 0;
     uint8_t* temp_ptr = 0;
     struct stat s    = {0};

     if( ( temp_fd = open( filename, O_RDONLY ) ) < 0 )
     {
          printf( "Cannot open '%s' : errno %d\\n", filename, errno );
          return false;
     }


     if( fstat( temp_fd, &s ) < 0 )
     {
          printf( "Cannot stat '%s' : errno %d\\n", filename, errno );
          return false;
     }

     if( ( temp_ptr   = (uint8_t*)mmap( NULL, 
                                      s.st_size,
                                      PROT_READ,
                                      MAP_PRIVATE,
                                      temp_fd,
                                      0 ) ) == MAP_FAILED )
     {
          printf( "Cannot map '%s' : errno %d\\n", filename, errno );
          close( temp_fd );
          return false;
     }

     m->map_fd   = temp_fd;
     m->map_size = s.st_size;
     m->map_ptr  = temp_ptr;
     m->mapped   = true;

     return true;
}

bool unmap_file( PMap m )
{
     if( m->mapped == true )
     {
          munmap( m->map_ptr, m->map_size );
          close( m->map_fd );
          m->mapped = false;
     }
     return true;
}

"""

'''
Create the solid line /***...***/ which forms the beginning
and end of a C comment block
'''
def make_solid_line():
    result = "/"
    for i in range( 0, COMMENT_BLOCK_COLUMN_SIZE-2 ):
        result += "*"
    result += "/\n"
    return result


'''
Create a single line of C comment block, optionally with text
'''
def make_comment_line(text=''):
    result = "/* "
    result += "%s" % text
    while( len(result) < COMMENT_BLOCK_COLUMN_SIZE-2 ):
        result += " "
    result += "*/\n"
    return result


'''
Create the comment block for the C source file
'''
def make_comment_block(title, other_information=""):
    result =  make_solid_line()
    for i in range(0, COMMENT_BLOCK_PRE_TEXT_BLANK_LINES ):
        result += make_comment_line()
    result += make_comment_line(title)
    result += make_comment_line( datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
    result += make_comment_line(other_information)
    for i in range(0, COMMENT_BLOCK_POST_TEXT_BLANK_LINES ):
        result += make_comment_line()
    result += make_solid_line()
    return result


'''
Create the includes block for the C source file
'''
def make_includes(includes=()):
    result =  "#include <stdio.h>\n"
    result += "#include <stdint.h>\n"
    for i in includes:
        result += "#include <%s>\n" % i
    return result


'''
Create the main() function for the C source file
'''
def make_main_function(filename):
    result =  "int main( int argc, char* argv[] )\n"
    result += "{\n"
    result += "     printf( \"%%s\\n\", \"%s\" );\n" % filename
    result += "     return 0;\n"
    result += "}\n\n"
    return result

'''
Create the main() function for the C source file - with call to file open
'''
def make_main_function_with_file_map(filename):
    result =  "int main( int argc, char* argv[] )\n"
    result += "{\n"
    result += "     int retVal = -1;\n"
    result += "     Map input = {0};\n"
    result += "\n"
    result += "     if( argc < 2 )\n"
    result += "     {\n"
    result += "          printf( \"Usage: %%s <inputfile>\\n\", \"%s\");\n" % filename
    result += "          retVal = 0;\n"
    result += "          goto end;\n"
    result += "     }\n"
    result += "\n"
    result += "     if( map_file( argv[1], &input ) == false )\n"
    result += "     {\n"
    result += "          goto end;\n"
    result += "     }\n"
    result += "\n"
    result += "     retVal = 0;\n"
    result += "end:\n"
    result += "     unmap_file( &input );\n"
    result += "     return retVal;\n"
    result += "}\n\n"
    return result

'''
Create the Makefile
'''
def make_makefile(filestem, path_and_filename, files=[]):
    result = "all:\n\t"
    result += "gcc -o %s " % filestem
    for i in files:
        result += "%s " % i
    result += "\n"
    # write it to the file
    try:
        with open( path_and_filename, "w+" ) as fh:
            fh.write(result)
    except Exception as e:
        print( "Error: %s\n" % e )
        return False
    
    return True


'''
Create a C source file
'''
def make_c_file(filestem, path_and_filename, include_header=False, include_utility=False):
    
    # assemble the file contents
    result =  make_comment_block(filestem)
    result += make_includes()
    if( include_header == True ):
        result += "#include \"%s.h\"\n" % filestem
    if( include_utility == True ):
        result += "#include \"%s.h\"\n" % UTILITY_HEADER
    result += "\n\n"
    if( include_utility == True ):
        result += make_main_function_with_file_map(filestem)
    else:
        result += make_main_function(filestem)

    # write it to the file
    try:
        with open( path_and_filename, "w+" ) as fh:
            fh.write(result)
    except Exception as e:
        print( "Error: %s\n" % e )
        return False

    return True

'''
Create a C header file
'''
def make_c_header(filestem, path_and_filename):
    # assemble the file contents
    result =  make_comment_block(filestem)
    result += '#pragma once\n\n'
    result += "\n\n"
    result += "#define AUTO_BUILD_NAME \"%s\"\n" % filestem
    result += "#define AUTO_BUILD_DATE \"%s\"\n" % ( datetime.now().strftime("%Y-%m-%d") )
    result += "#define AUTO_BUILD_TIME \"%s\"\n" % ( datetime.now().strftime("%H:%M:%S") )
    result += "\n\n"
    # write it to the file
    try:
        with open( path_and_filename, "w+" ) as fh:
            fh.write(result)
    except Exception as e:
        print( "Error: %s\n" % e )
        return False

    return True

'''
Create utility header
'''
def make_utility_header(filestem, path_and_filename):
    result = make_comment_block("UTILITY FUNCTIONS - AUTOGENERATED HEADER")
    result += "\n\n"
    result += utility_header

    # write it to the file
    try:
        with open( path_and_filename, "w+" ) as fh:
            fh.write(result)
    except Exception as e:
        print( "Error: %s\n" % e )
        return False

'''
Create utility code
'''
def make_utility_code(filestem, path_and_filename):
    result = make_comment_block("UTILITY FUNCTIONS - AUTOGENERATED SOURCE")
    result += "\n\n"
    result += utility_code

    # write it to the file
    try:
        with open( path_and_filename, "w+" ) as fh:
            fh.write(result)
    except Exception as e:
        print( "Error: %s\n" % e )
        return False

'''
The main() function - parse arguments, create directory, call other functions
'''
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stem", help="Name of program. Source and header will be named this.")
    parser.add_argument( "-d", "--create_header", help="Add a header file", action="store_true")
    parser.add_argument( "-m", "--create_makefile", help="Add a makefile", action="store_true")
    parser.add_argument( "-u", "--create_utility_functions", help="Add a file containing utility functions", action="store_true")

    args = parser.parse_args()

    # get the current directory - we will make our directory here
    current_directory = getcwd()
    stem = args.stem


    file_list = []
    path = current_directory + '/' + stem
    mkdir(path) 
    c_source_path_filename = "%s/%s.c" % ( path, stem )
    file_list.append( "%s.c" % stem )
    c_header_path_filename = ""
    makefile_path_filename = ""

    if args.create_utility_functions:
        utility_header_path_filename = "%s/%s.h" % ( path, UTILITY_HEADER )
        utility_code_path_filename   = "%s/%s.c" % ( path, UTILITY_SOURCE )
        file_list.append( "%s.c" % UTILITY_SOURCE )

        if( make_utility_header( stem, utility_header_path_filename ) == False ):
            print( "Error creating utility header file" )
            exit(-1)
        
        if( make_utility_code( stem, utility_code_path_filename ) == False ):
            print( "Error creating utility source code file" )
            exit(-1)

    if args.create_header:
        c_header_path_filename = "%s/%s.h" % ( path, stem )
    
    if args.create_makefile:
        makefile_path_filename = "%s/Makefile" % path

    if( make_c_file( stem, c_source_path_filename, args.create_header, args.create_utility_functions ) == False ):
        print( "Error creating C source file" )
        exit(-1)

    if( args.create_header ):
        if( make_c_header( stem, c_header_path_filename ) == False ):
            print( "Error creating header file" )
            exit(-1)

    if( args.create_makefile ):
        if( make_makefile( stem, makefile_path_filename, file_list ) == False ):
            print( "Error creating Makefile" )
            exit(-1)

    print( "[Ok]" ) 


if __name__ == "__main__":
    main()