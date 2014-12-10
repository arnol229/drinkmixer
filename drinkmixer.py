import RPi.GPIO as GPIO
import SocketServer
from time import sleep

#Debug
recipes = {
    "rumMix":{"rum":1,"orange_juice":2,"sour_mix":1},
    #"rum mix":{"rum":1,"coke":1,"orange_juice":2,"sour_mix":1},
    #"vodka mix":{"vodka":1,"orange_juice":2}
}

#################### Program Starts #####################

class DrinkMixer():

    def __init__(self):

        # Members
        self.bottle_assignments = {"rum":7,"vodka":23,"orange_juice":24,"sour_mix":25}
        self.valid_recipes = []

        # Set GPIO mode
        GPIO.setmode(GPIO.BCM)

        # Set up pins on GPIO
        # Input
        # Outputs
        GPIO.setup(7, GPIO.OUT)
        GPIO.setup(25, GPIO.OUT)
        GPIO.setup(24, GPIO.OUT)
        GPIO.setup(23, GPIO.OUT)

        # Init state
        GPIO.output(7, GPIO.LOW)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(23, GPIO.LOW)

    # Function: List Whats on Tap
    # Inputs: none
    # Output: Liquor, Port
    # Purpose: Lists out whats on tap for the user.
    def List_Bottles(self):
        for liquid, port in self.bottle_assignments.iteritems():
            print "Bottle " + str(port) + " is currently assigned " + liquid

    # Function: Dynamic Bottle Assignments
    # Inputs: Liquor, Port
    # Output: none
    # Purpose: Changes bottles the user sets from their phone.
    def Assign_Bottle(self, liquid, port):
        self.bottle_assignments[liquid] = port

    # Function: Mix Recipe
    # Inputs: Recipe
    # Output: Physical Pumping
    # Purpose: Take a *Valid* recipe and outputs.
    def Mix_Recipe(self, recipe):
        for liquid, seconds in recipe.iteritems():
            print "port is: " + liquid
            print "seconds to run is: " + str(seconds)
            GPIO.output(self.bottle_assignments[liquid],GPIO.HIGH)
            sleep(seconds)
            GPIO.output(self.bottle_assignments[liquid],GPIO.LOW)

    # Function: Make Recipe Bank
    # Inputs: Current Bottle Assignments
    # Output: List of Possible Recipes Based on Current Assignments
    # Purpose: 
    def Make_Recipe_Bank(self, bottle_assignments):
        on_hand = self.bottle_assignments.keys()

        # Append to this list any possible recipes
        self.valid_recipes

        #TODO
        # Grab Recipes from text file
        for recipe_name, ingredients in recipes.iteritems():
            # Iterate through all recipes
            if all (liquid in on_hand for liquid in ingredients):
                for liquid in ingredients:
                    print "We know this is in there: " + liquid
            else:
                for liquid, seconds in ingredients.iteritems():
                    if not liquid in on_hand:
                        print "We dont have this: " + liquid

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def refreshRecipes(self):
        return "Command to refresh recipes within the ROM bank."

    def makeDrink(self, commandInputs):
        self.server.mixer.Mix_Recipe(recipes[commandInputs[1]])
        return "Success."
     
    def changeTaps(self):
        return "Command to change what is on tap."

    def listTaps(self):
        self.server.mixer.List_Bottles()
        return "Success."
     
    def mixerHelp(self):
        return "The commands available are 'bank', 'make', 'list', and 'change'."

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
    
        # Try returning a command from our dictionary
        commandInputs = str.split(self.data)

        if(commandInputs[0] == "bank"):
            response = self.refreshRecipes()
        elif(commandInputs[0] == "make"):
            response = self.makeDrink(commandInputs)
        elif(commandInputs[0] == "list"):
            response = self.listTaps()
        elif(commandInputs[0] == "change"):
        	response = self.changeTaps()
        else:
        	response = self.mixerHelp()
        self.request.sendall(response)

class MyServer(SocketServer.ThreadingTCPServer):

    def __init__(self, server_address, RequestHandlerClass, mixer):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.mixer = mixer


####################### Main #######################

if __name__ == "__main__":
    HOST, PORT = "", 9999

    try:
        # Sets up GPIO for a mixer machine
        mixer = DrinkMixer()

        # Create the server, binding to localhost on port 9999
        #server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
        server = MyServer((HOST, PORT), MyTCPHandler, mixer)

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
    finally:
        GPIO.cleanup()
        #server.shutdown()
