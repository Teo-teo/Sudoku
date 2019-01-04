
import random
import curses
import argparse
from curses import wrapper
import time
from threading import Thread 
import operator
import sys



welcome = ['\\\    \\\    // ||=== ||    ||=== //===\\\ |\  /| ||===\n',
            ' \\\  //\\\  //  ||==  ||    ||    ||   || ||\/|| ||== \n',
            '  \\\//  \\\//   ||=== ||=== ||=== \\\===// ||  || ||===']


loser = ['\\\  // //===\\\  ||   ||  ||    //===\\\ //==  ||===',
           ' \\\//  ||   ||  ||   ||  ||    ||   || ||=\\\ ||== ',
            '  ||   \\\===//  \\\===//  ||=== \\\===//  ==// ||===']


winner = ['\\\  // //===\\\  ||   ||  \\\    \\\    // || |\  ||',
           ' \\\//  ||   ||  ||   ||   \\\  //\\\  //  || ||\\\||',
            '  ||   \\\===//  \\\===//    \\\//  \\\//   || || \\\|']


class Gui () :


    stdscr = None

    table_offset_x = 20

    table_offset_y = 2


    def __init__ (self):


        self.stdscr = curses.initscr ()  # start curses window

        curses.use_default_colors ()  # use default black screen color

        curses.noecho () 

        curses.cbreak ()  # application react to keys instantly without requiring the Enter key to be pressed

        self.stdscr.keypad ( True )  # enable curses to use special keys such as Page UP or home ...




    def terminate (self):

        curses.nocbreak ()

        self.stdscr.keypad ( False )

        curses.echo ()

        curses.endwin () 


    def menu (self):

        difficult = 1

        try:

            for y, string in zip ( range (2,5), welcome ):

                self.stdscr.addstr ( y,13, string, curses.A_REVERSE )

            self.stdscr.addstr ( 6, 25, 'Sudoku game developed by Matteo Piacentini')


            self.stdscr.addstr ( 10, 2, 'EASY', curses.A_UNDERLINE )

            self.stdscr.addstr ( 12, 2, 'MEDIUM', curses.A_UNDERLINE )

            self.stdscr.addstr ( 14, 2, 'HARD', curses.A_UNDERLINE )

            self.stdscr.refresh ()


            difficult = self.selectdifficultmode ()


        except KeyboardInterrupt as interrupt : pass

        except curses.error as error : 
            
            self.stdscr.clear ()

            self.menu ()

        finally:

            self.stdscr.clear ()

            self.stdscr.refresh ()

    

    def selectdifficultmode (self):
            
        while True :

            difficult = 3

            y = self.stdscr.getyx () [0]

            key = self.stdscr.getch ()

        
            if key == curses.KEY_RIGHT: return difficult


            elif key == curses.KEY_UP and y is not 10: 
                
                self.stdscr.move ( y - 2, 2  )

                difficult = difficult - 1

            elif key == curses.KEY_DOWN and y is not 14: 
                
                self.stdscr.move ( y + 2, 2 )

                difficult = difficult + 1

            
            elif key == curses.KEY_RESIZE: self.stdscr.refresh ()

            else: continue



    def create_table (self):

        for pos in range (10):

            if pos % 3 is 0:

                self.stdscr.move ( 0 + self.table_offset_y, ( pos * 4 ) + self.table_offset_x )

                self.stdscr.vline ( '|', 19 )  # print vertical line at cursor position


        for pos in range (10):

            if pos % 3 is 0:

                self.stdscr.move (( pos * 2 ) + self.table_offset_y, 0 + self.table_offset_x )

                self.stdscr.hline ( '-', 37 )   # print horizontal line at cursor position 


        self.stdscr.refresh ()  



    def print (self,sudoku):

        table = sudoku.get_full_table ()

        hide_table = sudoku.get_hide_table ()

        for r in range (9):

            for k in range (9):

                if k in hide_table [r] :

                    self.stdscr.addch (( k * 2 + 1 ) + self.table_offset_y, ( r * 4 + 2 ) + self.table_offset_x, '%d' %table [r][k] )

        
        self.stdscr.refresh ()



    def insert (self,sudoku) :


        table = self.get_coordinates ()

        hide_table = sudoku.get_hide_table ()

        raw = 0; column = 0

        try:

            while True :


                coordinates = table.get ((raw,column))

                number = self.stdscr.getch ( coordinates [0], coordinates [1] )


                if number == curses.KEY_DOWN: raw = 8 if raw is 8 else raw + 1  # move bottom on pressed key down

                elif number == curses.KEY_RIGHT: column = 8 if column is 8 else column + 1  # move right on pressed key right

                elif number == curses.KEY_LEFT: column = 0 if column is 0 else column - 1  # move left on pressed key left

                elif number == curses.KEY_UP: raw = 0 if raw is 0 else raw - 1  # move top on pressed key top

                else:
                    
                    if chr (number).isdigit () and raw not in hide_table [column] :  # raw and column are inverted !!!
                    
                        self.stdscr.addch ( number )  # print on table only if number inserted

                        sudoku.insert_result_table (int(chr(number)),column,raw)  # insert number in table   !!!!! POSSIBLE INDEX ERROR !!!

                    else: continue
                

                self.stdscr.refresh ()  # refresh table

                time.sleep ( 0.1 )


        except (ValueError,curses.error) as error: pass

        except KeyboardInterrupt as close :

            result_table = sudoku.get_result_table ()

            full_table = sudoku.get_full_table ()

            try :

                self.stdscr.clear ()

                if self.equals ( result_table, full_table ) is True: self.winner ()

                else: self.loser ()

            except KeyboardInterrupt as exit : sys.exit (0)



    def equals (self,result_table,full_table):   # return True if tables are equals else return False

        correct_raw = 0

        for groupA, groupB in zip ( full_table, result_table ):

            if operator.eq ( groupA, groupB ): correct_raw = correct_raw + 1

        
        if correct_raw is 9: return True

        else: return False



    def winner (self):

                
        for y, string in zip ( range (8,11), winner ):

            self.stdscr.addstr ( y,13, string, curses.A_REVERSE )

        self.stdscr.refresh ()

        time.sleep (5)

    
    def loser (self):
        
        for y, string in zip ( range (8,11), loser ):

            self.stdscr.addstr ( y,13, string, curses.A_REVERSE )

        self.stdscr.refresh ()

        time.sleep (5)


    
    def get_coordinates (self) :

        table = dict ()  # create table with position matrix as key and position inside window curses as value


        for rindex in range (9) :

            for kindex in range (9) :

                coordinates = ((( kindex * 2 + 1 ) + self.table_offset_y ), (( rindex * 4 + 2 ) + self.table_offset_x ))  # set that contains number coordinates
 
                table.update ({( kindex,rindex ) : coordinates }) #insert number position and coordinates in table


        return table



    def getstdscr (self): return self.stdscr  # get main window




class Sudoku () :

    
    table = list ()  # originally table

    hide_table = list ()  # create new table with some number from originally table

    result_table = list ()


    def __init__ ( self, n ):
        
        
        for r in range (9):

            void_list = list ()

            for k in range (9):

                void_list.insert (k,-1)

            self.table.insert (r,void_list)


        for r in range (9):

            void_list = list ()

            for k in range (9):

                void_list.insert (k,-1)

            self.result_table.insert (r,void_list)



        self.table [0] = self.generatefirstraw ()

        for index,number in zip ( range (1,9), self.generatefirstcolumn () ) :

            self.table [index][0] = number 

        
        self.generate_full_table ()

        self.generate_hide_table (n)

        self.generate_result_table ()



    
    def insertnumber ( self, number, rindex, kindex ):

        for i in range ( 0,9 ):

            if number == self.table [ rindex ][ kindex ]: continue 

            if number == self.table [ rindex ] [i] or number == self.table [i] [ kindex ]: return False


        return True 




    def generate_full_table ( self ) :

        try:

            for r in range (1,9):

                for k in range (1,9):


                    number = random.randint (1,9)  # genera un numero casuale da 1 a 9

                    attempts = 1  # tentativi


                    while not self.insertnumber (number,r,k):  # while number is not correct

                        if attempts is 10:  # se i tentativi provati superano i 9 vuol dire che non è stato possibile aggiungere un numero a quella casella
                            
                            raise Exception ()  # solleva un'eccezione e rinizia da capo


                        number = 1 if number is 9 else number + 1  # aggiorna il numero secondo un ciclo da 1 a 9

                        attempts = attempts + 1  # aggiorna ad ogni tentativo il numero di tentativi provati


                    self.table [r][k] = number  # se non è stata sollevata nessuna eccezione vuol dire che il numero è corretto, viene inserito nella tabella nella specifica posizione


        except Exception as error : 

            for r in range (1,9):  # clear table without clear first colums and first raw

                for k in range (1,9): 

                    self.table [r][k] = -1

            
            self.generate_full_table ()

            

    def generate_hide_table (self,n):

        for r in range (9):

            self.hide_table.append ( random.choices ( population = [0,1,2,3,4,5,6,7,8], k = n ))   # get casual number from matrix raw



    def generate_result_table (self):

        for r in range (9):

            for k in range (9):

                if k in self.hide_table [r]: self.result_table [r][k] = self.table [r][k]

                else: self.result_table [r][k] = -1



    def get_full_table (self): return self.table

    def get_hide_table (self): return self.hide_table

    def get_result_table (self): return self.result_table

    def insert_result_table (self,number,posY,posX): self.result_table [posY][posX] = number

    def generatefirstraw (self): return random.sample ( range (1,10), 9 )



    def generatefirstcolumn (self):

        choices = [ 1,2,3,4,5,6,7,8,9 ]

        choices.remove ( self.table [0][0] )  # rimuovi dalle possibili scelte l'elemento in posizione (0,0)

        return random.sample ( choices, 8 )


    
        

def setdifficult (selection):

    if selection is 1 : return 5

    elif selection is 2 : return 4

    else : return 3



def start ( stdscr ) :


    parser = argparse.ArgumentParser ()

    parser.add_argument ( "-d", dest = 'difficult', required = False, default = 1, type = int, help = 'Game difficult' )


    args = parser.parse_args ()


    gui = Gui ()  # initialize GUI

    selection = gui.menu ()  # get difficult from menu

    sudoku = Sudoku ( setdifficult (selection) )

    gui.create_table ()

    gui.print ( sudoku )

    gui.insert ( sudoku )



    

    



if __name__ == '__main__':

    wrapper ( start )  # useful for restoring terminal when application dies ( such as when code is buggy and raises an uncaught exception )