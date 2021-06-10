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
        else:
            print(f'Cannot mark this mine {cell} because is not in the sentence {self.cells} or count {self.count} is not >0')
            raise ValueError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells-={cell}
        else:
            print(f'Cannot mark this safe {cell} because is not in the sentence {self.cells} ')
            raise ValueError

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
                self.available_moves.add(i,j)

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
                if 0<=i<self.height and 0<=j<self.width and i,j!=(cell):
                    neighbors.add((i,j))
        return neighbors

    def add_to_set(self, cells, mine_or_safe):
        """
        :param cells: takes in cells to add to set
        :param mine_or_safe: receives str 'mine' or 'safe'
        """
        if mine_or_safe=='mine':
            for cell in cells:
                self.mines.add(cell)
        elif mine_or_safe=='safe':
            for cell in cells:
                self.safes.add(cell)
        else:
            raise ValueError


    def find_conclusion_sentences(self):
        """
        find sentences that can draw conclusions, adds mines or safes to list
        and removes sentence from knowledge base
        """
        for sentence in self.knowledge:
            new_mines=sentence.known_mines()
            new_safes=sentence.known_safes()
            if len(new_mines)>0:
                self.add_to_set(new_mines, 'mine')
            elif len(new_safes)>0:
                self.add_to_set(new_safes, 'safe')
            else:
                continue #skips next lines and goes to next sentence todo check
            self.knowledge.remove(sentence)

    def aplica_aplica_subsets(self): #todo
        raise NotImplementedError

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


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        try:
            safe_move=self.safes.pop()
        except:
            return None
        return safe_move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        self.available_moves=self.available_moves-self.moves_made-self.mines
        try:
            random_move=self.available_moves.pop()
        except:
            return None
        return random_move



if __name__=="__main__":
    game=Minesweeper()
    sentence1=Sentence({(1,1), (2,2), (3,3), (4,4)},3)
    sentence2 = Sentence({(1, 1), (2,2)}, 1)
    sentence3 = Sentence({(3, 3), (4, 4)}, 2)
    sentence4=Sentence({(2,1), (3,2), (4,3), (5,4)},0)
    knowledge=[sentence1, sentence2, sentence3, sentence4]
    for s in knowledge:
        print(f'known mines {s.known_mines()}')
        print(f'known safes {s.known_safes()}')
        for m in s.known_mines():
            s.mark_mine(m)
        for sf in s.known_safes():
            s.mark_safe(sf)
        print(f'known mines {s.known_mines()}')
        print(f'known safes {s.known_safes()}')

