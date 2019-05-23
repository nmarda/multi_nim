from graphics import *
from math import *
import time
import numpy as np
import itertools

STONE_DIAMETER = 40
STONE_COLOR = "blue"
SQUARE_WIDTH = STONE_DIAMETER + 10
NUM_ROWS = 4
NUM_COLS = 4
SCREEN_WIDTH = NUM_COLS * SQUARE_WIDTH + 100
SCREEN_HEIGHT = NUM_ROWS * SQUARE_WIDTH + 100

def clickedCircle(circ, click):
	center = circ.getCenter()
	return sqrt((center.getX() - click.getX()) ** 2 + (center.getY() - click.getY()) ** 2) <= STONE_DIAMETER // 2

def createCircles(win):
	#draw the grid of circles on the window
	circles = []
	for x in range(SQUARE_WIDTH // 2, SQUARE_WIDTH * NUM_COLS, SQUARE_WIDTH):
		column = []
		for y in range(SQUARE_WIDTH // 2, SQUARE_WIDTH * NUM_ROWS, SQUARE_WIDTH):
			circ = Circle(Point(x, y), STONE_DIAMETER // 2)
			circ.setFill(STONE_COLOR)
			circ.setOutline(STONE_COLOR)
			circ.draw(win)
			column += [circ]
		circles += [column]
	return circles

def createLines(win):
	top = 0
	bottom = NUM_ROWS * SQUARE_WIDTH
	left = 0
	right = NUM_COLS * SQUARE_WIDTH
	for x in range(left, right + 1, SQUARE_WIDTH):
		line = Line(Point(x, top), Point(x, bottom))
		line.draw(win)
	for y in range(top, bottom + 1, SQUARE_WIDTH):
		line = Line(Point(left, y), Point(right, y))
		line.draw(win)

def clickedBox(click):
	return NUM_COLS * SQUARE_WIDTH + 10 <= click.getX() <= NUM_COLS * SQUARE_WIDTH + 90 and 10 <= click.getY() <= 90

def doTurn(circles, turn):
	newBoard = []
	for col in circles:
		newBoard.append(circles[:])
	for column in range(len(circles)):
		for circle in circles[column]:
			if circle in turn:
				newBoard[column].remove(circle)
	return newBoard

def performComputerTurn(circles):
	comp_moves = getLegalMoves(circles)
	for move in comp_moves: #if this loop runs 0 times, no legal moves for computer (so loss)
		newBoard = doTurn(circles, move)
		human_moves = getLegalMoves(newBoard)
		alwaysWins = True
		for human in human_moves: # if no human moves, then it's a win for the computer
			human_board = doTurn(newBoard, human)
			isWin, _ = performComputerTurn(human_board):
			if not isWin:
				alwaysWins = False
				break
		if alwaysWins:
			return True, move
	return False, None

def playGame():
	win = GraphWin("Nim Player Interface", SCREEN_WIDTH, SCREEN_HEIGHT)
	createLines(win)
	
	endTurn = Rectangle(Point(NUM_COLS * SQUARE_WIDTH + 10, 90), Point(NUM_COLS * SQUARE_WIDTH + 90, 10))
	endTurn.setFill("red")
	endTurn.draw(win)
	player_text = Text(Point(NUM_COLS * SQUARE_WIDTH + 50, 50), "Player 1's turn")
	player_text.draw(win)
	player_1_wins = 0
	player_2_wins = 0
	player_1_win_text = Text(Point(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 67), "Player 1 wins: 0")
	player_1_win_text.draw(win)
	player_2_win_text = Text(Point(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 33), "Player 2 wins: 0")
	player_2_win_text.draw(win)
	while(True):
		circles = createCircles(win)
		player_1_turn = True
		player_text.setText("Player 1's turn")
		endTurn.setFill("red")
		tiles_removed = 0
		row_selection = -1
		col_selection = -1

		while circles != [[] for i in range(NUM_COLS)]:
			print(circles)
			getLegalMoves(circles)
			click = win.getMouse()
			if clickedBox(click):
				if tiles_removed != 0:
					tiles_removed = 0
					player_1_turn = not player_1_turn
					endTurn.setFill("red")
					player_text.setText("Player 1's turn" if player_1_turn else "Player 2's turn")
					row_selection = -1
					col_selection = -1
					performComputerTurn(circles)
					player_1_turn = True
			else:
				print(len(circles))
				for column in range(len(circles)):
					for circ in circles[column]:
						if clickedCircle(circ, click):
							row, col = circ.getCenter().getY(), circ.getCenter().getX()
							if row_selection == -1 and col_selection == -1:
								row_selection, col_selection = row, col
							elif row_selection == row:
								col_selection = -1
							elif col_selection == col:
								row_selection = -1
							else:
								circ.setFill("black")
								time.sleep(1)
								circ.setFill(STONE_COLOR)
								break
							tiles_removed += 1
							endTurn.setFill("green")
							circles[column].remove(circ)
							circ.undraw()
							break
		if player_1_turn:
			player_2_wins += 1
			player_2_win_text.setText("Player 2 wins: " + str(player_2_wins))
		else:
			player_1_wins += 1
			player_1_win_text.setText("Player 1 wins: " + str(player_1_wins))
	win.getMouse()
	win.close()

def circToArrayIndex(circle):
	return int((circle.getCenter().getY())/SQUARE_WIDTH), int((circle.getCenter().getX() - SQUARE_WIDTH/2.0)/SQUARE_WIDTH)

def arrayIndexToCirc(row, col, circles):
	for entry in circles[col]:
		row_i, col_i = circToArrayIndex(entry)
		print(row_i, col_i)
		if row_i == row:
			return entry
	return None

def getIndicatorArray(circles):
	array = [[0] * NUM_ROWS for i in range(NUM_COLS)]
	for column in circles:
		for entry in column:
			row, col = circToArrayIndex(entry)
			array[col][row] = 1
	return(array)	

def getLegalMoves(circles):
	array = getIndicatorArray(circles)
	output = []
	#EVERY ROW
	for k in range(len(array[0])):
		has_one = []
		for i in range(len(array)):
			if array[i][k] == 1:
				has_one.append(i)
		row_options = []
		for r in range(1, len(has_one) + 1):
			for combo in itertools.combinations(has_one, r):
				appending_array = [0]*NUM_COLS
				# print(combo)
				for i in combo:
					appending_array[i] = 1
				# print(appending_array)
				row_options.append(appending_array)
		for entry in row_options:
			output_array = [[0] * NUM_ROWS for i in range(NUM_COLS)]
			for i in range(len(output_array[k])):
				output_array[i][k] = entry[i]
			output.append(output_array)
	#EVERY COLUMN
	for k in range(len(array)):
		has_one = []
		for i in range(len(array[k])):
			if array[k][i] == 1:
				has_one.append(i)
		col_options = []
		for r in range(1, len(has_one) + 1):
			for combo in itertools.combinations(has_one, r):
				appending_array = [0]*NUM_ROWS
				# print(combo)
				for i in combo:
					appending_array[i] = 1
				# print(appending_array)
				col_options.append(appending_array)
		for entry in col_options:
			output_array = [[0] * NUM_ROWS for i in range(NUM_COLS)]
			for i in range(len(output_array[k])):
				output_array[k][i] = entry[i]
			output.append(output_array)
	output_pruned = []
	for entry in output:
		if entry not in output_pruned:
			output_pruned.append(entry)
	print(output_pruned)
	output_final = []
	for entry in output_pruned:
		append_array = []
		for j in range(len(entry)):
			for i in range(len(entry[j])):
				if entry[j][i] == 1:
					append_array.append(arrayIndexToCirc(i, j, circles))
		output_final.append(append_array)
	print(output_final)


	#create indicator array



# def doTurn(circles, circles):


if __name__ == "__main__":
	playGame()










































