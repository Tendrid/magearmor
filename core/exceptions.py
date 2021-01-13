class PlayerErrorMessage(Exception):
    def __init__(self, message, player=None):
        self.message = message
        self.player = player

    def __str__(self):
        return self.message
