from finsim.group import Group
from finsim.person import Person

class Simulation:
    def __init__(self, data):
        self.group_mode = data.group_mode
        if self.group_mode:
            self.model = Group(data)
        else:
            self.model = Person(data.get_people()[0])
        self.month = 0
        self._assign_savings_goal()

    def simulate(self):
        goal_met = False
        while not goal_met:
            self.month += 1
            goal_met = self._step_forward()
        
    def _step_forward(self):
        if (self.month % 12) == 1:
            self.model.begin_year()

        self.model.simulate_month()
        if self._achieved_goal():
            return True

        if (self.month % 12) == 0:
            self.model.end_year()
        else:
            if self.model.updated:
                self.model.strategise()

        return False

    def _achieved_goal(self):
        return self.model.total_saved() >= self.savings_goal

    def _assign_savings_goal(self):
        # TODO: Collect from user
        # TODO: Though, allow predefinition using the datafile
        self.savings_goal = 45000
        