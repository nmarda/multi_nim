from graphics import *
from math import *
import time
import numpy as np
import itertools
from random import *

#recommended running:   python3 NimPlayer.py t f t f 4 4
#						python3 NimPlayer.py t t t t 8 8 (try and beat it!)

COMPUTER_FIRST = sys.argv[1][0] in ['T', 't']
PLAY_YOURSELF = sys.argv[2][0] in ['T', 't']
GRAPHICS = sys.argv[3][0] in ['T', 't'] or PLAY_YOURSELF
CLEAR_MEMO_EVERY_GAME = sys.argv[4][0] in ['T', 't']
NUM_ROWS = int(sys.argv[-1])
NUM_COLS = int(sys.argv[-2])

STONE_DIAMETER = 40
STONE_COLOR = "blue"
SQUARE_WIDTH = STONE_DIAMETER + 10
SCREEN_WIDTH = max(NUM_COLS * SQUARE_WIDTH + 100, 220)
SCREEN_HEIGHT = max(NUM_ROWS * SQUARE_WIDTH + 167, 220)
Total_time = 0
player_moves = []
computer_moves = []
useBeta = False
useRandSpeedUP = True


"""
graphics handling, etc
"""

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
			if GRAPHICS:
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

def clickedExit(click):
	return NUM_COLS * SQUARE_WIDTH + 20 <= click.getX() <= NUM_COLS * SQUARE_WIDTH + 80 and 160 <= click.getY() <= 200

def clickedBox(click):
	return NUM_COLS * SQUARE_WIDTH + 10 <= click.getX() <= NUM_COLS * SQUARE_WIDTH + 90 and 10 <= click.getY() <= 90

"""
symmetry rules
"""
def getRow(indicator, row_to_get):
	ans = [[col[row_to_get]] for col in indicator]

def getRows(indicator, bot_row):
	ans = [[col[i] for i in range(bot_row, len(indicator[0]))] for col in indicator]
	return ans

def biggestRow(indicator):
	row_lengths = [sum([1 for col in range(indicator.shape[0]) if indicator[col][row] == 1]) for row in range(indicator.shape[1])]
	# print("biggestRow indicator", indicator)
	# print("row_lengths", row_lengths)
	# print("---")
	max_row = max(row_lengths)
	ans = [i for i in range(indicator.shape[1]) if row_lengths[i]==max_row][0]
	# print("ans", ans)
	return ans

def biggestCol(indicator):
	# print("biggestCol indicator", indicator)
	col_lengths = [sum([1 for row in range(indicator.shape[1]) if indicator[col][row] == 1]) for col in range(indicator.shape[0])]
	max_col = max(col_lengths)
	ans = [i for i in range(indicator.shape[0]) if col_lengths[i]==max_col][0]
	# print("biggestCol:", ans)
	return ans

def orderRowsAndCols(indicator):
	bot_row = 0
	while bot_row < indicator.shape[1]:
		big_row_ind = bot_row + biggestRow(indicator[:, bot_row:])
		temp = np.copy(indicator[:, big_row_ind])
		indicator[:, big_row_ind] = indicator[:, bot_row]
		indicator[:, bot_row] = temp
		bot_row += 1
	left_col = 0
	while left_col < indicator.shape[0]:
		big_col_ind = left_col + biggestCol(indicator[left_col:])
		temp = np.copy(indicator[big_col_ind])
		indicator[big_col_ind] = indicator[left_col]
		indicator[left_col] = temp
		left_col += 1
	return indicator

# def isCircSym(circle_indicator):
# 	indicator = np.array(circle_indicator)
# 	ans = np.array_equal(indicator, np.rot90(indicator, 2))
# 	# if ans:
# 	# 	print("ans")
# 	return ans

def makeSymmetry(indicator, isBeta):
	"""
	takes in indicator array, returns string
	"""
	# nicePrint(indicator)
	indicator = getIndicatorArray(indicator)
	indicator = np.array(indicator)
	indicator = orderRowsAndCols(indicator)
	# print(indicator.sum())
	if indicator.sum() == 0: return
	bot_row = 0
	left_col = 0
	indicator_len = indicator.shape[1]
	while bot_row < indicator_len:
		# print("bot_row", bot_row)
		# print("indicator before row swap:", indicator)
		# print("indicator in makeSym from 1 up:", indicator[:][1:])
		# print("indicator in makeSym from bot_row up:", indicator[:, bot_row:])
		big_row_ind = bot_row + biggestRow(indicator[:, bot_row:])
		# print(indicator[:][big_row_ind])
		temp = np.copy(indicator[:, big_row_ind])
		# temp = indicator[:][big_row_ind]
		indicator[:, big_row_ind] = indicator[:, bot_row]
		indicator[:, bot_row] = temp
		threshold = bot_row + 1
		# print("temp:", temp)
		# print("indicator after row swap:", indicator)
		#gravity that boi
		bottom_row_has_one = [i for i in range(left_col, NUM_COLS) if indicator[i, bot_row] == 1]
		curr_col = left_col
		while curr_col < NUM_COLS - 1 and bottom_row_has_one != []:
			if indicator[curr_col, bot_row] != 1:
				temp = np.copy(indicator[curr_col])
				indicator[curr_col] = indicator[bottom_row_has_one[0]]
				indicator[bottom_row_has_one[0]] = temp
				# print("in between:", indicator, curr_col, left_col, bottom_row_has_one)
			bottom_row_has_one.pop(0)
			curr_col += 1
		# print("indicator after row gravity:", indicator)
		# for i in range(indicator_len):
		# 	print(indicator[i][bot_row])
		arr = [i for i in range(indicator.shape[0]) if indicator[i][bot_row] == 1]
		if arr == []: break
		right_col = max(arr)
		# print("right_col", right_col)
		while left_col < right_col:# and indicator[left_col][bot_row] == 1:
			big_col_ind = left_col + biggestCol(indicator[left_col:right_col + 1, bot_row:]) 
			temp = np.copy(indicator[left_col])
			indicator[left_col] = indicator[big_col_ind]
			indicator[big_col_ind] = temp
			#gravity that boi
			left_col_has_one = [i for i in range(threshold, NUM_ROWS) if indicator[left_col][i] == 1]
			curr_row = threshold
			while curr_row < NUM_ROWS - 1 and left_col_has_one != []:
				if indicator[left_col][curr_row] != 1:
					temp = np.copy(indicator[:, curr_row])
					indicator[:, curr_row] = indicator[:, left_col_has_one[0]]
					indicator[:, left_col_has_one[0]] = temp
				left_col_has_one.pop(0)
				curr_row += 1
			threshold += 1
			left_col += 1
			# if threshold >= right_col:
			# 	left_col = right_col + 1
			# 	break
		left_col += 1
		bot_row = threshold
	if NUM_ROWS == NUM_COLS:
		trans = stringifyIndicator(indicator.T.tolist())
		if isBeta and trans in winForCurrPlayerBeta.keys() or not isBeta and trans in winForCurrPlayer.keys():
			return trans
	# if random() < .0001:
	# 	print(indicator)
	return stringifyIndicator(indicator.tolist())

def nicePrint(arr):
	for col in arr:
		print(col)

"""
basic computer turn
"""

def circleCount(circles):
	count = 0
	for col in circles:
		count += len(col)
	return count

def doTurn(circles, turn):
	newBoard = []
	for col in range(len(circles)):
		newBoard.append(circles[col][:])
	for column in range(len(circles)):
		for circle in circles[column]:
			if circle in turn:
				newBoard[column].remove(circle)
	return newBoard

winForCurrPlayer = {} # dict from board to (win_for_first_player, moves)
winForCurrPlayerBeta = {} # dict from board to (is_sure, (num_wins, num_losses))

def stringifyIndicator(indicator):
	# ans = str(NUM_ROWS)
	ans = ""
	for col in indicator:
		for circ in col:
			ans += str(circ)
	return ans


def stringify(circles):
	# ans = str(NUM_ROWS)
	ans = ""
	for col in getIndicatorArray(circles):
		for circ in col:
			ans += str(circ)
	return ans

counter = 0

def performComputerTurnPerfectHelper(circles):
	global counter
	counter += 1
	circle_indicator = makeSymmetry(circles, False)
	# if isCircSym(getIndicatorArray(circles)):
	# 	return False
	if circle_indicator in winForCurrPlayer.keys():
		return winForCurrPlayer[circle_indicator]
	legal_moves = getLegalMoves(circles)
	for move in legal_moves:
		newBoard = doTurn(circles, move)
		if not performComputerTurnPerfectHelper(newBoard):
			winForCurrPlayer[circle_indicator] = True
			return True
	winForCurrPlayer[circle_indicator] = False
	return False

def performComputerTurnPerfect(circles, winner_predict, win, compTurn):
	
	global Total_time
	# time.sleep(1)
	# return True, choice(getLegalMoves(circles))
	start_time = time.time()
	if GRAPHICS:
		loading = Text(Point(NUM_COLS * SQUARE_WIDTH + 50, 140), "Thinking...")
		loading.draw(win)
	for move in getLegalMoves(circles):
		newCircles = doTurn(circles, move)
		isWin = not performComputerTurnPerfectHelper(newCircles)
		if isWin:
			if GRAPHICS:
				loading.undraw()
			winner_predict.setText("Computer will win!" if compTurn else "Player will win!")
			Total_time += time.time() - start_time
			# print("--- %s seconds ---" % (time.time() - start_time))
			return True, move
	if GRAPHICS:
		loading.undraw()
	winner_predict.setText("Player will win!" if compTurn else "Computer will win!")
	Total_time += time.time() - start_time
	# print(counter)
	return False, None

def performComputerTurnBetaHelper(circles, num_moves):
	# global counting
	# counting += 1
	circle_indicator = makeSymmetry(circles, True)
	if circle_indicator in winForCurrPlayerBeta.keys() and winForCurrPlayerBeta[circle_indicator][0]:
		return winForCurrPlayerBeta[circle_indicator][1][1] == 0 #means no false values
	if num_moves == 0:
		print("error1")
		if circle_indicator in winForCurrPlayerBeta.keys():
			_, (win, loss) = winForCurrPlayerBeta[circle_indicator] #isSure is necessarily false here.
			ans = beta.pdf(win, loss)
		else:
			ans = beta.pdf(1, 1)
		return ans
	legal_moves = getLegalMoves(circles)
	max_win_prob = 0
	for move in legal_moves:
		newBoard = doTurn(circles, move)
		move_win_prob = 1 - performComputerTurnBetaHelper(newBoard, num_moves - 1)
		if move_win_prob > max_win_prob:
			if move_win_prob == 1:
				winForCurrPlayerBeta[circle_indicator] = True, (1, 0)
				return 1
			else:
				print("error3")
				max_win_prob = move_win_prob
	if max_win_prob == 0:
		winForCurrPlayerBeta[circle_indicator] = True, (0, 1)
	else:
		print("error4")
	return max_win_prob

def performComputerTurnBeta(circles, winner_predict, win, compTurn):
	global Total_time
	
	# time.sleep(1) 
	# return True, choice(getLegalMoves(circles))
	start_time = time.time()
	# loading = Text(Point(NUM_COLS * SQUARE_WIDTH + 50, 140), "Thinking...")
	# loading.draw(win)
	max_win_prob = 0
	max_win_move = None
	max_new_circles = None
	legalMoves = getLegalMoves(circles)
	tempCount = 0
	for move in legalMoves:
		newCircles = doTurn(circles, move)
		winProb = 1 - performComputerTurnBetaHelper(newCircles, 3)
		if winProb == 1:
			# loading.undraw()
			winner_predict.setText("Computer will win!" if compTurn else "Player will win!")
			Total_time += time.time() - start_time
			# print("--- %s seconds ---" % (time.time() - start_time))
			# winForCurrPlayerBeta[stringifyIndicator(getIndicatorArray(circles))] = True, (1, 0)
			return 1, move
		if winProb != 0:
			print("Error2")
		if max_win_prob < winProb:
			max_win_prob = winProb
			max_win_move = move
			max_new_circles = newCircles
	# loading.undraw()
	if max_win_prob == 0:
		winner_predict.setText("Player will win!" if compTurn else "Computer will win!")
	elif max_win_move != None:
		if compTurn:
			computer_moves.append(max_new_circles)
		else:
			player_moves.append(max_new_circles)
	Total_time += time.time() - start_time
	# print(counter)
	return max_win_prob, max_win_move

def performHumanTurnPerfect(circles, winner_predict, win):
	global Total_time
	# return True, choice(getLegalMoves(circles))
	start_time = time.time()
	# loading = Text(Point(NUM_COLS * SQUARE_WIDTH + 50, 140), "Thinking...")
	# loading.draw(win)
	for move in getLegalMoves(circles):
		newCircles = doTurn(circles, move)
		isWin = not performComputerTurnHelper3(newCircles)
		if isWin:
			# loading.undraw()
			winner_predict.setText("Player will win!")
			Total_time += time.time() - start_time
			return True, move
	# loading.undraw()
	winner_predict.setText("Computer will win!")
	Total_time += time.time() - start_time
	# print(counter)
	return False, None

def addResults(boards, isWin):
	for board in boards:
		temp = winForCurrPlayerBeta.get(board, (False, (1, 1)))
		# print(temp)
		temp[1][isWin] += 1
		winForCurrPlayerBeta[board] = temp
		# print(winForCurrPlayerBeta[board])

"""
general gameplay
"""

def playGame():
	win = GraphWin("Nim Player Interface", SCREEN_WIDTH, SCREEN_HEIGHT)
	createLines(win)
	
	endTurn = Rectangle(Point(NUM_COLS * SQUARE_WIDTH + 10, 90), Point(NUM_COLS * SQUARE_WIDTH + 90, 10))
	endTurn.setFill("red")
	endTurn.draw(win)
	exitGame = Rectangle(Point(NUM_COLS * SQUARE_WIDTH + 20, 200), Point(NUM_COLS * SQUARE_WIDTH + 80, 160))
	exitGame.setFill("yellow")
	exitGame.draw(win)
	exit_text = Text(Point(NUM_COLS * SQUARE_WIDTH + 50, 180), "Exit")
	exit_text.draw(win)
	player_text = Text(Point(NUM_COLS * SQUARE_WIDTH + 50, 50), "Player's turn")
	player_text.draw(win)
	winner_predict = Text(Point(NUM_COLS * SQUARE_WIDTH + 50, 110), "Who's gonna win?")
	winner_predict.draw(win)
	player_1_wins = 0
	player_2_wins = 0
	player_1_win_text = Text(Point(NUM_COLS * SQUARE_WIDTH // 2, SCREEN_HEIGHT - 100), "Player wins: 0")
	player_1_win_text.draw(win)
	player_2_win_text = Text(Point(NUM_COLS * SQUARE_WIDTH // 2, SCREEN_HEIGHT - 67), "Computer wins: 0")
	player_2_win_text.draw(win)
	average_time_text = Text(Point(NUM_COLS * SQUARE_WIDTH // 2, SCREEN_HEIGHT - 33), "Average Time: 0")
	average_time_text.draw(win)
	first_player_text = Text(Point(NUM_COLS * SQUARE_WIDTH // 2, SCREEN_HEIGHT - 133), "First player: " + ("computer" if COMPUTER_FIRST else "player"))
	first_player_text.draw(win)
	total_runs = 0
	while(True):		
		FIRST_MOVE = True
		print(counter)
		if CLEAR_MEMO_EVERY_GAME:
			winForCurrPlayer.clear()
			winForCurrPlayerBeta.clear()
		if total_runs > 0:
			average_time_text.setText("Average Time: {0:.3f}".format((Total_time / total_runs)))
		total_runs += 1
		# winner_predict.setText("Who will win?")
		circles = createCircles(win)
		player_turn = not COMPUTER_FIRST
		player_text.setText("Player's turn")
		endTurn.setFill("red")
		tiles_removed = 0
		row_selection = -1
		col_selection = -1
		# makeSymmetry(getIndicatorArray(circles))
		# if COMPUTER_FIRST:
		# 	comp_win, moves = performComputerTurnPerfect(circles, winner_predict, win, True)
		# 	if not comp_win:
		# 		moves = choice(getLegalMoves(circles))
		# 	for move in moves:
		# 		row, col = circToArrayIndex(move)
		# 		circles[col].remove(move)
		# 		if GRAPHICS:
		# 			move.undraw()
		# 	if circles != [[] for _ in range(NUM_COLS)]:
		# 		player_turn = True 
		# 		player_text.setText("Player's turn" if player_turn else "Computer's turn")

		while circles != [[] for i in range(NUM_COLS)]:
			if not PLAY_YOURSELF:
				if useRandSpeedUp and circleCount(circles) > 16: #NUM_COLS * NUM_ROWS / 5:
					moves = getRandomMove(circles)
				else:
					if player_turn and useBeta:
						is_win, moves = performComputerTurnBeta(circles, winner_predict, win, not player_turn)
					else:
						is_win, moves = performComputerTurnPerfect(circles, winner_predict, win, not player_turn)
					if moves is None:
						moves = choice(getLegalMoves(circles))
				for move in moves:
					row, col = circToArrayIndex(move)
					circles[col].remove(move)
					if GRAPHICS:
						move.undraw()
				player_turn = not player_turn


				# # print(circles)
				# getLegalMoves(circles)

		# This section is used if you want to play yourself
			else:
				if COMPUTER_FIRST and FIRST_MOVE:
					if useRandSpeedUP and circleCount(circles) > 16:# NUM_COLS * NUM_ROWS / 5:
						moves = getRandomMove(circles)
					else:
						comp_win, moves = performComputerTurnPerfect(circles, winner_predict, win, True)
						if not comp_win:
							moves = choice(getLegalMoves(circles))
					for move in moves:
						row, col = circToArrayIndex(move)
						circles[col].remove(move)
						if GRAPHICS:
							move.undraw()
					if circles != [[] for _ in range(NUM_COLS)]:
						player_turn = True 
						player_text.setText("Player's turn" if player_turn else "Computer's turn")
						FIRST_MOVE = False

				click = win.getMouse()
				if clickedBox(click):
					if tiles_removed != 0:
						tiles_removed = 0
						player_turn = not player_turn
						endTurn.setFill("red")
						player_text.setText("Player's turn" if player_turn else "Computer's turn")
						row_selection = -1
						col_selection = -1
						# makeSymmetry(getIndicatorArray(circles))
						if useRandSpeedUP and circleCount(circles) > 16: #NUM_COLS * NUM_ROWS / 5:
							moves = getRandomMove(circles)
						else:
							comp_win, moves = performComputerTurnPerfect(circles, winner_predict, win, True)
							if not comp_win:
								moves = choice(getLegalMoves(circles))
						for move in moves:
							row, col = circToArrayIndex(move)
							circles[col].remove(move)
							move.undraw()

						if circles != [[] for _ in range(NUM_COLS)]:
							player_turn = True
							player_text.setText("Player's turn" if player_turn else "Computer's turn")
				elif clickedExit(click):
					return
				else:
					# print(len(circles))
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
									circ.setFill("red")
									time.sleep(1)
									circ.setFill(STONE_COLOR)
									break
								tiles_removed += 1
								endTurn.setFill("green")
								circles[column].remove(circ)
								circ.undraw()
								break

		if not player_turn: #actually means the player just moved, i.e. won
			player_1_wins += 1
			player_1_win_text.setText("Player wins: " + str(player_1_wins))
			addResults(player_moves, 1)
			addResults(computer_moves, 0)
		else:
			player_2_wins += 1
			player_2_win_text.setText("Computer wins: " + str(player_2_wins))
			addResults(player_moves, 0)
			addResults(computer_moves, 1)
		FIRST_MOVE = True
	win.getMouse()
	win.close()

"""
various Helper Methods
"""

def circToArrayIndex(circle):
	return int((circle.getCenter().getY())/SQUARE_WIDTH), int((circle.getCenter().getX() - SQUARE_WIDTH/2.0)/SQUARE_WIDTH)

# def circArrayToMatrixIndex()

def arrayIndexToCirc(row, col, circles):
	for entry in circles[col]:
		row_i, col_i = circToArrayIndex(entry)
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

moveStorage = {}

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
			for i in range(len(output_array)):
				output_array[i][k] = entry[i]
			output.append(output_array)
	# print(output)
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
	# print(output_pruned)
	# moveStorage[stringifyIndicator(array)] = output_pruned
	output_final = []
	for entry in output_pruned:
		append_array = []
		for j in range(len(entry)):
			for i in range(len(entry[j])):
				if entry[j][i] == 1:
					append_array.append(arrayIndexToCirc(i, j, circles))
		output_final.append(append_array)
	if [] in output_final:
		output_final.remove([])
	# print(output_final)
	return output_final

def getCircles(indicator, circles):
	if np.sum(indicator) == 0:
		# print("yep")
		return []
	return [arrayIndexToCirc(col, row, circles) for row in range(len(indicator)) for col in range(len(indicator[0])) if indicator[row][col] == 1]

def getRandomMove(circles):
	indicator = np.array(getIndicatorArray(circles))
	# print(indicator)
	if random() < .5:
		col = -1
		while col == -1 or sum(indicator[col]) == 0:
			col = int(floor(random() * len(indicator)))
		pick = []
		while pick == []:
			pick = [i for i in range(indicator.shape[1]) if indicator[col, i] == 1 and random() < 0.5]
		# print(pick)
		ret = [arrayIndexToCirc(i, col, circles) for i in pick]
	else:
		row = -1
		while row == -1 or sum(indicator[:, row]) == 0:
			row = int(floor(random() * len(indicator[0])))
		pick = []
		while pick == []:
			pick = [i for i in range(indicator.shape[0]) if indicator[i, row] == 1 and random() < 0.5]
		# print(pick)
		ret = [arrayIndexToCirc(row, i, circles) for i in pick]
	# print(ret)
	return ret

if __name__ == "__main__":
	playGame()












































