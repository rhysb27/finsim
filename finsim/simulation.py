from finsim.group import Group
from finsim.person import Person
from finsim.ui import UI

class Simulation:
    def __init__(self, data):
        self.group_mode = data.group_mode
        if self.group_mode:
            self.model = Group(data)
        else:
            self.model = Person(data.get_people()[0])
        self.month = 0

        goal_from_data = data.savings_goal
        if goal_from_data is not None:
            self.savings_goal = goal_from_data
        else:
            self.savings_goal = UI.obtain_savings_goal()

    def simulate(self):
        goal_met = False
        while not goal_met:
            self.month += 1
            goal_met = self._step_forward()
        # TODO: Construct and save final report
        UI.end(self.month)
        
        
    def _step_forward(self):
        if (self.month % 12) == 1:
            self.model.begin_year()

        self.model.simulate_month()
        if self._achieved_goal():
            return True

        if (self.month % 12) == 0:
            self.model.end_year()
            UI.end_year(self.model, self.month // 12)
        else:
            if self.model.updated:
                self.model.strategise()

        return False

    def _achieved_goal(self):
        return self.model.total_saved() >= self.savings_goal
        