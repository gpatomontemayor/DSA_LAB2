# -*- coding: utf-8 -*-

from binarytree import BinaryTree, Node
from binarysearchtree import BSTNode, BinarySearchTree

import csv  # read files csv, tsv
import os.path  # to work with files and directory https://docs.python.org/3/library/os.path.html
import queue  # package implementes a queueu, https://docs.python.org/3/library/queue.html
import re  # working with regular expressions


def checkFormatHour(time):
    """checks if the time follows the format hh:dd"""
    pattern = re.compile(r'\d{2}:\d{2}')  # busca la palabra foo

    if pattern.match(time):
        data = time.split(':')
        hour = int(data[0])
        minute = int(data[1])
        if hour in range(8, 20) and minute in range(0, 60, 5):
            return True

    return False


# number of all possible appointments for one day
NUM_APPOINTMENTS = 144


class Patient:
    """Class to represent a Patient"""
    def __init__(self, name, year, covid, vaccine, appointment=None):

        self.name = name
        self.year = year
        self.covid = covid
        self.vaccine = vaccine
        self.appointment = appointment  # string with format hour:minute

    def setAppointment(self, time):
        """gets a string with format hour:minute"""
        self.appointment = time

    def __str__(self):
        return self.name + '\t' + str(self.year) + '\t' + str(
            self.covid) + '\t' + str(self.vaccine) + '\t appointment:' + str(
                self.appointment)

    def __eq__(self, other):
        return other is not None and self.name == other.name


class HealthCenter2(BinarySearchTree):
    """Class to represent a Health Center. This class is a subclass of a
    binary search tree to achive a better temporal complexity of its
    algorithms for searching, inserting o removing a patient (or an
    appointment)"""
    def __init__(self, filetsv=None, orderByName=True):
        """
        This constructor allows to create an object instance of HealthCenter2.
        It takes two parameters:
        - filetsv: a file csv with the information about the patients whe
        belong to this health center
        - orderByName: if it is True, it means that the patients should be
        sorted by their name in the binary search tree, however, if is is
        False, it means that the patients should be sorted according
        their appointments
        """

        # Call to the constructor of the super class, BinarySearchTree.
        # This constructor only define the root to None
        super(HealthCenter2, self).__init__()

        # Now we
        if filetsv is None or not os.path.isfile(filetsv):
            # If the file does not exist, we create an empty tree
            # (health center without patients)
            self.name = ''
            # print('File does not exist ',filetsv)
        else:
            order = 'by appointment'
            if orderByName:
                order = 'by name'

            self.name = filetsv[filetsv.rindex('/') + 1:].replace('.tsv', '')
            # self.name='LosFrailes'

            fichero = open(filetsv)
            lines = csv.reader(fichero, delimiter="\t")

            for row in lines:
                # print(row)
                name = row[0]  # nombre
                year = int(row[1])  # año nacimiento
                covid = False
                if int(row[2]) == 1:  # covid:0 o 1
                    covid = True
                vaccine = int(row[3])  # número de dosis
                try:
                    appointment = row[4]
                    if not checkFormatHour(appointment):
                        appointment = None

                except:
                    appointment = None

                objPatient = Patient(name, year, covid, vaccine, appointment)
                # name is the key, and objPatient the eleme
                if orderByName:
                    self.insert(name, objPatient)
                else:
                    if appointment:
                        self.insert(appointment, objPatient)
                    else:
                        print(
                            objPatient,
                            " was not added because appointment was not",
                            " valid!!!"
                        )

            fichero.close()

    def searchPatients(self, year=2021, covid=None, vaccine=None):
        """return a new object of type HealthCenter 2 with the patients who
        satisfy the criteria of the search (parameters).
        The function has to visit all patients, so the search must follow
        a level traverse of the tree. If you use a inorder traverse,
        the resulting tree should be a list!!!"""

        # Complexity O(nlogn).
        # Best case: tree is empty or calling tree is not ordered by name.
        # Worst case: no worst case. We have to traverse all the tree in
        # any other case.

        result = HealthCenter2()

        if self._root is None:
            print('tree is empty')
        else:
            # Check if calling tree is ordered by time
            if checkFormatHour(self._root.key):
                print(
                    "Calling tree is ordered by time. It must be by name"
                    )
                return result

            trav = BinaryTree()  # Binary tree used as a list
            trav._root = Node(self._root)  # Add the root to list-tree
            next_trav = trav._root  # Next element to retrieve from list-tree
            last_trav = trav._root  # Last element of the list-tree

            while next_trav is not None:  # O(n). Traverse the tree-list
                # Get the next element of the tree-list
                current = next_trav.elem
                if current.elem.year <= year and (
                        current.elem.covid == covid
                        or covid is None) and (current.elem.vaccine == vaccine
                                               or vaccine is None):
                    # If it satisfies the requirements, add to the end
                    result.insert(current.elem.name,
                                  current.elem)  # log(n) function
                if current.left is not None:
                    # Add to the end of the tree-list to check afterwards
                    last_trav.right = Node(current.left, parent=last_trav)
                    # Update last element of the tree-list
                    last_trav = last_trav.right
                if current.right is not None:
                    # Add to the end of the tree-list to check afterwards
                    last_trav.right = Node(current.right, parent=last_trav)
                    # Update last element of the tree-list
                    last_trav = last_trav.right
                # Get next element of the tree-list to check
                next_trav = next_trav.right

        return result

    def vaccine(self, name, vaccinated):
        """This functions simulates the vaccination of a patient whose
        name is name.
        It returns True is the patient is vaccinated and False eoc"""

        # Complexity O(logn).
        # Best case: calling tree is empty or is not ordered by name.
        # Another possibility is that the patient we want to find is the root
        # and it hasn't received any vaccines.
        # Worst case: Finding a patient with 1 or more dosages and not being
        # a leaf for removing it.

        # Check if calling tree is ordered by time
        if checkFormatHour(self._root.key):
            print(
                "Calling tree is ordered by time. It must be by name"
                )
            return False

        node = self.find(name)  # O(logn) look for the patient with key (name)
        if node is None:
            print(
                "{} does not exist in the calling health center".format(name))
            return False
        elif node.elem.vaccine == 2:
            print("{} has already received two vaccines".format(name))
            self._remove(
                node
            )  # patient is fully vaccinated so, eliminate it from HealthCenter
            newPat = Patient(name, node.elem.year, node.elem.covid, 2)
            vaccinated.insert(
                name, newPat)  # and add it to the vaccinated health center
            return False
        elif node.elem.vaccine == 1:
            self._remove(
                node)  # after vaccinated, the patient would have the 2 doses
            newPat = Patient(name, node.elem.year, node.elem.covid, 2)
            vaccinated.insert(
                name, newPat)  # so add them to the vaccinated health center
            return True
        else:
            node.elem.vaccine = 1  # Update the number of dosages
            return True

    def makeAppointment(self, name, time, schedule):
        """This functions makes an appointment
        for the patient whose name is name. It functions returns True
        is the appointment is created and False eoc """

        # Complexity O(nlogn).
        # Best case: calling tree is empty or is not ordered by name,
        # schedule is ordered by name or inputed time has an invalid format.
        # Another possibility is that the patient we want to find is the
        # root in the calling tree and has already received two vaccines, or
        # that it hasn't and the schedule tree is empty.
        # Worst case: Finding a patient with less than the two dosages and
        # the first available slot is at the beginning or at the end (the
        # contrary to the inputed time).

        # Check if calling tree is ordered by time
        if checkFormatHour(self._root.key):
            print(
                "Calling tree is ordered by time. It must be by name"
                )
            return False

        # Check if schedule tree is ordered by time
        if checkFormatHour(schedule._root.key) is False:
            print(
                "Schedule tree is ordered by name. It must be by time"
                )
            return False
        # Check the format of the inputed time (hh:mm)
        if checkFormatHour(time) is False:
            print("Time format is not correct. Format: hh:mm")
            return False

        # Look for the patient in the calling Health Center
        node = self.find(name)  # O(logn)

        # We first check the error cases (no patient or already
        # vaccinated patient)
        if node is None:
            print(
                "{} does not exist in the calling health center".format(name))
            return False
        elif node.elem.vaccine == 2:
            print("{} has already received two vaccines".format(name))
            return False
        else:  # O(nlogn)
            if schedule._root is None:  # Empty tree so add it directly
                node.elem.setAppointment(
                    time)  # Change time in calling health center
                schedule.insert(time, node.elem)  # Add it to the schedule BST
                return True
            elif schedule.search(
                    time
            ) is False:
                # The slot is free, so assign it to the patient requesting it
                node.elem.setAppointment(
                    time)  # Change time in calling health center
                schedule.insert(time, node.elem)  # Add it to the schedule BST
                return True
            else:
                # The total number of possible time slots is 144, we check
                # whether they are all occupied
                if schedule.size() == NUM_APPOINTMENTS:  # O(n)
                    print(
                        "{} cannot be appointed for a vaccine since there are",
                        " no time slots"
                        .format(name))
                    return False
                else:
                    print(
                        "Already someone at {}. Looking for best fit"
                        .format(time))

                    # Modify the variables to find the previous and next slot
                    # taking into account the hour and minutes format if they
                    # go over the limits (prevTime < 08:00 or nextTime > 19:55)
                    # it will return None.

                    prevTime = prevSlot(time)
                    nextTime = nextSlot(time)

                    # Loop until we get to the extremes O(n)
                    while prevTime or nextTime:

                        # First we look if the previous slot is available
                        if prevTime:
                            if schedule.search(prevTime) is False:  # O(logn)
                                # If the time cannot be found, the previous
                                # time is assigned for this patient
                                node.elem.setAppointment(prevTime)
                                schedule.insert(
                                    prevTime,
                                    node.elem)  # add it to the schedule BST
                                print(
                                    "Created appointment for {} at {}".format(
                                        name, prevTime))
                                return True
                            else:
                                # Modify to get the previous time slot
                                prevTime = prevSlot(prevTime)

                        # Look if the afterwards slot is available
                        if nextTime:
                            if schedule.search(nextTime) is False:
                                # If the time cannot be found, this next time
                                # is assigned for this patient
                                node.elem.setAppointment(nextTime)
                                schedule.insert(
                                    nextTime,
                                    node.elem)  # add it to the schedule BST
                                print(
                                    "Created appointment for {} at {}".format(
                                        name, nextTime))
                                return True
                            else:
                                # Modify to get the next time slot
                                nextTime = nextSlot(nextTime)

                        # The end of the loop will never be reached since it's
                        # checked before whether or not the tree is full


def prevSlot(time):
    """Method to compute the previous time slot. If getting out of range
    (before 08:00), returns None O(1)"""
    # Split the inputed data into hour and minutes
    data = time.split(":")
    hour = int(data[0])
    minutes = int(data[1]) - 5  # Update minutes

    if minutes < 0:  # We have to substract one hour
        prevTime = "{:02d}:{:02d}".format(hour - 1, 55)
    else:
        prevTime = "{:02d}:{:02d}".format(hour, minutes)

    if checkFormatHour(prevTime):  # Check if time is in the range
        return prevTime
    else:
        return None


def nextSlot(time):
    """Method to compute the previous time slot. If getting out of range
    (before 08:00), returns None. O(1)"""
    # Split the inputed data into hour and minutes
    data = time.split(":")
    hour = int(data[0])
    minutes = int(data[1]) + 5  # Update minutes

    if minutes > 55:  # We have to add one hour
        nextTime = "{:02d}:{:02d}".format(hour + 1, 0)
    else:
        nextTime = "{:02d}:{:02d}".format(hour, minutes)

    if checkFormatHour(nextTime):  # Check if in range
        return nextTime
    else:
        return None


if __name__ == '__main__':

    # Testing the constructor. Creating a health center where patients are
    # sorted by name
    o = HealthCenter2('data/LosFrailes2.tsv')
    o.draw()
    print()

    print(
        'Patients who were born in or before than 1990, had covid and did',
        ' not get any vaccine'
    )
    result = o.searchPatients(1990, True, 0)
    result.draw()
    print()

    print(
        'Patients who were born in or before than 1990, did not have covid',
        ' and did not get any vaccine'
    )
    result = o.searchPatients(1990, False, 0)
    result.draw()
    print()

    print('Patients who were born in or before than 1990 and got one dosage')
    result = o.searchPatients(1990, None, 1)
    result.draw()
    print()

    print('Patients who were born in or before than 1990 and had covid')
    result = o.searchPatients(1990, True)
    result.draw()
    print()

    # Testing the constructor. Creating a health center where patients
    # are sorted by name
    schedule = HealthCenter2('data/LosFrailesCitas.tsv', False)
    schedule.draw()
    print()

    o.makeAppointment("Perez", "08:00", schedule)
    o.makeAppointment("Losada", "19:55", schedule)
    o.makeAppointment("Jaen", "16:00", schedule)
    o.makeAppointment("Perez", "16:00", schedule)
    o.makeAppointment("Jaen", "16:00", schedule)

    o.makeAppointment("Losada", "15:45", schedule)
    o.makeAppointment("Jaen", "08:00", schedule)

    o.makeAppointment("Abad", "08:00", schedule)
    o.makeAppointment("Omar", "15:45", schedule)

    schedule.draw()
    vaccinated = HealthCenter2('data/vaccinated.tsv')
    vaccinated.draw(False)

    name = 'Ainoza'  # doest no exist
    result = o.vaccine(name, vaccinated)
    print("was patient vaccined?:", name, result)
    print('center:')
    o.draw(False)
    print('vaccinated:')
    vaccinated.draw(False)

    name = 'Abad'  # 0 dosages
    result = o.vaccine(name, vaccinated)
    print("was patient vaccined?:", name, result)
    print('center:')
    o.draw(False)
    print('vaccinated:')
    vaccinated.draw(False)

    name = 'Font'  # with one dosage
    result = o.vaccine(name, vaccinated)
    print("was patient vaccined?:", name, result)
    print('center:')
    o.draw(False)
    print('vaccinated:')
    vaccinated.draw(False)

    name = 'Omar'  # with two dosage
    result = o.vaccine(name, vaccinated)
    print("was patient vaccined?:", name, result)
    print('center:')
    o.draw(False)
    print('vaccinated:')
    vaccinated.draw(False)
