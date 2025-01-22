
'''
This protocol decoder prints the hex dump of a binary signal for a given 
Baud rate.
This can be useful when there is no previous knowledge about the digital
signal, so that it can be better analized and first guess on the type of 
signal given. 

Note: This decoder only works for Baud rates which are factors of the 
sampling frequency.
'''

from .pd import Decoder
