import pickle as p

NAME = 0
POINT_DIFFS = 1
WINS = 2
MATCHES = 3

class LeaderBoard(object):
    def __init__(self):
        self.file = "leaderlist.dat"
        with open(self.file, "ab") as _:
            pass



    @staticmethod
    def win_percentage(person):
        return float(person[WINS] * 100) / person[MATCHES]


    @staticmethod
    def compare_leaders(person_1, person_2):
        return cmp((LeaderBoard.win_percentage(person_1), person_1[POINT_DIFFS], person_1[WINS]),
                    (LeaderBoard.win_percentage(person_2), person_2[POINT_DIFFS], person_2[WINS]))

    @staticmethod
    def sort(array):
        return sorted(array, cmp=LeaderBoard.compare_leaders, reverse=True)

    def get_top_number(self, number):
        with open(self.file, "rb") as f:
            raw_leaders = LeaderBoard.sort(p.load(f))[:number]

        new_leaders = []
        prev_leader = ["Batman", 0, 2, 1]
        rank = 0
        count = 1
        for leader in raw_leaders:
            if LeaderBoard.compare_leaders(leader, prev_leader) == -1:
                rank += count
                count = 1
            else:
                count += 1

            new_leaders.append(
                [rank, leader[NAME], leader[MATCHES], leader[WINS], leader[MATCHES] - leader[WINS], leader[POINT_DIFFS], LeaderBoard.win_percentage(leader)]
            )

            prev_leader = leader

        return new_leaders

    def store_match_result(self, name, point_diff):
        with open(self.file, "rb") as f:
            try:
                people = p.load(f)
            except:
                people = []

        for person in people:
            if person[NAME].lower() == name.lower():
                person[MATCHES] += 1
                person[POINT_DIFFS] += point_diff
                if point_diff > 0:
                    person[WINS] += 1
                break
        else:
            people.append([name, point_diff, 1 if point_diff > 0 else 0, 1])

        with open(self.file, "wb") as f:
            p.dump(people, f)


