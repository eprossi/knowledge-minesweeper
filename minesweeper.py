#FINAL VERSION - DEBUGGED - WORKING

import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        # sets a flag that this is a new/changed Sentence to try and subtract from others if subset
        self.changed=True

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return {cell for cell in self.cells if len(self.cells)==self.count}

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return {cell for cell in self.cells if self.count==0}

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells and self.count>0:
            self.cells-={cell}
            self.count-=1
            #flags this sentence as having been changed - to try again to subtract if subset of others
            self.changed=True


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells-={cell}
            self.changed=True


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

        # creates available moves set
        self.available_moves=set()
        for i in range (height):
            for j in range (width):
                self.available_moves.add((i,j))

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def neighboring_cells(self, cell):
        """
        receives a cell and returns all neighboring cells
        """
        neighbors=set()
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if 0<=i<self.height and 0<=j<self.width and (i,j)!=(cell):
                    neighbors.add((i,j))
        return neighbors


    def find_conclusion_sentences(self):
        """
        find sentences that can draw conclusions, adds mines or safes to list
        and removes sentence from knowledge base
        """
        for sentence in self.knowledge:
            new_mines=sentence.known_mines()
            new_safes=sentence.known_safes()
            if len(new_mines)>0:
                for mine in new_mines:
                    self.mark_mine(mine)
            elif len(new_safes)>0:
                for safe in new_safes:
                    self.mark_safe(safe)
            else:
                continue #skips next lines and goes to next sentence
            # if known_mines or safes is successful, all cells are marked mine or safe
            # then "concluded" sentence can be removed from knowledge base
            self.knowledge.remove(sentence) # only runs when if or elif is true because of "continue"

    def subtract_subset(self):
        """
        every time a new knowledge is added by add_knowledge, this method is run
        it will run in a loop util there are no more changed sentences
        sentences can be changed by it's own creation, or when new mines or safes are found
        everytime a sentence is changed, this method tries to subtract it from the other
        sentences if it is a subset of them.
        """
        while True:
            #resets flag for entire METHOD.
            subset_change=False
            for sub_sentence in self.knowledge:
                # runs for each SENTENCE flagged
                if sub_sentence.changed:
                    sub_sentence.changed=False #clears flag of the sub_sentence being subtracted
                    for sentence in self.knowledge:
                        # checks if sentence is a subset of all the others and if it is not itself (equal len)
                        if sub_sentence.cells.issubset(sentence.cells) and len(sub_sentence.cells)<len(sentence.cells):
                            sentence.cells-=sub_sentence.cells
                            sentence.count-=sub_sentence.count
                            sentence.changed=True #flags sentences being changed by the subtraction
                            subset_change=True #if there was any change - flags the METHOD to run one more time.
            if not subset_change:
                break
        # after all changes possible with the subsets, checks if there are new conclusions
        self.find_conclusion_sentences()

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        #finds neighbors and removes safes
        neighbors=self.neighboring_cells(cell)
        neighbors-=self.safes

        # stores len of neighbors to see how many mines took out
        old_neighbors_len=len(neighbors)
        #remove known mines
        neighbors-=self.mines
        #adjusts count by removing number of mines taken out
        count-=(old_neighbors_len-len(neighbors))
        #instances a new sentence and appends to knowledge base
        self.knowledge.append(Sentence(neighbors,count))
        #given that there is a new "changed" sentence, runs subtract subset method
        # to try and subtract this new sentence from all others of which it is subset.
        self.subtract_subset()


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for c in self.safes:
            if c not in self.moves_made:
                return c


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #used this set of available moves not to run the loop everytime.
        self.available_moves=self.available_moves-self.moves_made-self.mines
        try:
            random_move=self.available_moves.pop()
        except:
            return None
        return random_move
