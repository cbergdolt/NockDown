***************NockDown**************
By: Madeline Gent & Carolyn Bergdolt

------------------------------------

OVERVIEW:
You are a squirrel.
You have unlimited acorns.
You want to knock down as many targets as you can before your opponent squirrel.
The first squirrel to knock down 10 targets wins.

------------------------------------

HOW TO PLAY:
1) Player 1: Run "python play1.py" in your terminal window
2) Player 2: Run "python play2.py" in your terminal window
3) Move your squirrel left and right by using the arrow keys
4) Shoot your acorns at the targets when they appear by pressing the spacebar

------------------------------------

GAME INSPIRATION:
Our game was inspired by an activity in Donkey Kong Country 3: Dixie Kong's Double Trouble!
However, we wanted to add a little "Notre Dame flair," which is why
the targets are leprechauns and the players are overweight, overfed squirrels.

------------------------------------

NOTES:
Our main challenge was synching as many game features through the network 
connection (so as to avoid asyncronous game play/scoring) without sacrificing
game speed. This is why the scoring is controlled entirely in the play1.py 
program, which prevents player 1 and player 2 from exhibiting differing
scores in the case where both acorns are thrown almost simultaneously.
This is just one of the several places we introduced extra network communication.

------------------------------------

We hope you enjoyed playing our game as much as we enjoyed making it!
Thanks for a great semester!



