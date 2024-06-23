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
def make_c_file(filestem, path_and_filename, include_header=False):
    
    # assemble the file contents
    result =  make_comment_block(filestem)
    result += make_includes()
    if( include_header == True ):
        result += "#include \"%s.h\"\n" % filestem
    result += "\n\n"
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
The main() function - parse arguments, create directory, call other functions
'''
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stem", help="Name of program. Source and header will be named this.")
    parser.add_argument( "-d", "--create_header", help="Add a header file", action="store_true")
    parser.add_argument( "-m", "--create_makefile", help="Add a makefile", action="store_true")

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
    
    if args.create_header:
        c_header_path_filename = "%s/%s.h" % ( path, stem )
    
    if args.create_makefile:
        makefile_path_filename = "%s/Makefile" % path

    if( make_c_file( stem, c_source_path_filename, args.create_header ) == False ):
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