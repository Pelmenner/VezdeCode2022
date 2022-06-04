from typing import Tuple, Set, Dict
import threading

from datetime import datetime, timedelta
import discord
from discord.ext import commands
import pandas as pd

TOKEN = 'TOKEN'
bot = commands.Bot('ps.')

weekdays = {"понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3,
            "пятница": 4, "суббота": 5, "восресенье": 6}
classes = {}


class Class:
    def __init__(self, channel_name: str, days: str, time: str, students: str):
        self.channel_name = channel_name
        self.days = self._parse_weekdays(days)
        self.start_time, self.end_time = self._parse_time(time)
        self.students = students.split(",")
        self.attended = set()

        self._schedule_next_class(is_first=True)

    def finish(self):
        with open("log.txt", "a") as f:
            f.write(
                f"{self.channel_name} on {datetime.now().date()}: {', '.join(self.attended)}\n")
        self.attended.clear()
        self._schedule_next_class()

    def is_running(self) -> bool:
        current_time = datetime.now()
        return self.start_time < current_time < self.end_time

    def has_student(self, student: str) -> bool:
        return student in self.students

    def _schedule_next_class(self, is_first=False):
        date = datetime.now()
        if not is_first:
            date += timedelta(days=1)
        while date.weekday() not in self.days:
            date += timedelta(days=1)

        self.start_time = datetime.combine(date, self.start_time.time())
        self.end_time = datetime.combine(date, self.end_time.time())
        threading.Timer(
            (self.end_time - datetime.now()).total_seconds(), self.finish
        ).start()

    def register_attendance(self, student: str):
        self.attended.add(student)

    def _parse_weekdays(self, days: str) -> Set[int]:
        result = set()
        start, end = (weekdays.get(x, 0) for x in days.split(" - "))
        while start != end:
            result.add(start)
            start = (start + 1) % 7
        result.add(end)
        return result

    def _parse_time(self, time: str) -> Tuple[datetime, datetime]:
        start, end = time.split(" - ")
        return datetime.strptime(start, '%H:%M'), datetime.strptime(end, '%H:%M')


def load_classes(filename: str) -> Dict[str, Class]:
    classes = {}
    df = pd.read_csv(filename, header=None)
    for col in df.columns:
        class_args = df[col].tolist()
        classes[class_args[0]] = Class(*class_args)
    return classes


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState,
                                after: discord.VoiceState):
    channel = after.channel
    if before.channel == after.channel or not after.channel:
        return

    if channel.name not in classes:
        return

    current_class = classes[channel.name]
    if current_class.is_running() and current_class.has_student(member.display_name):
        current_class.register_attendance(member.display_name)


def main():
    global classes
    classes = load_classes("students.csv")
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
