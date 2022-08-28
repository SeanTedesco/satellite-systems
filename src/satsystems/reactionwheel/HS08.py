from .reactionwheel import Reactionwheel

class HS08(Reactionwheel):
    def __init__(self, uid, port, baud=115200, start_marker='<', end_marker='>'):
        super().__init__(uid, port, baud, start_marker, end_marker)
        self.logger.info(f'reaction wheel {uid} powered on')