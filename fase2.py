# -*- coding: utf-8 -*-

from binarysearchtree import BinarySearchTree

import csv  #read files csv, tsv
import os.path  #to work with files and directory https://docs.python.org/3/library/os.path.html
import queue  #package implementes a queueu, https://docs.python.org/3/library/queue.html
import re  #working with regular expressions


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


#number of all possible appointments for one day
NUM_APPOINTMENTS = 144


class Patient:
    """Class to represent a Patient"""
    def __init__(self, name, year, covid, vaccine, appointment=None):

        self.name = name
        self.year = year
        self.covid = covid
        self.vaccine = vaccine
        self.appointment = appointment  #string with format hour:minute

    def setAppointment(self, time):
        """gets a string with format hour:minute"""
        self.appointment = time

    def __str__(self):
        return self.name + '\t' + str(self.year) + '\t' + str(
            self.covid) + '\t' + str(self.vaccine) + '\t appointment:' + str(
                self.appointment)

    def __eq__(self, other):
        return other != None and self.name == other.name


class HealthCenter2(BinarySearchTree):
    """Class to represent a Health Center. This class is a subclass of a binary search tree to 
    achive a better temporal complexity of its algorithms for 
    searching, inserting o removing a patient (or an appointment)"""
    def __init__(self, filetsv=None, orderByName=True):
        """
        This constructor allows to create an object instance of HealthCenter2. 
        It takes two parameters:
        - filetsv: a file csv with the information about the patients whe belong to this health center
        - orderByName: if it is True, it means that the patients should be sorted by their name in the binary search tree,
        however, if is is False, it means that the patients should be sorted according their appointments
        """

        #Call to the constructor of the super class, BinarySearchTree.
        #This constructor only define the root to None
        super(HealthCenter2, self).__init__()

        #Now we
        if filetsv is None or not os.path.isfile(filetsv):
            #If the file does not exist, we create an empty tree (health center without patients)
            self.name = ''
            #print('File does not exist ',filetsv)
        else:
            order = 'by appointment'
            if orderByName:
                order = 'by name'

            #print('\n\nloading patients from {}. The order is {}\n\n'.format(filetsv,order))

            self.name = filetsv[filetsv.rindex('/') + 1:].replace('.tsv', '')
            #print('The name of the health center is {}\n\n'.format(self.name))
            #self.name='LosFrailes'

            fichero = open(filetsv)
            lines = csv.reader(fichero, delimiter="\t")

            for row in lines:
                #print(row)
                name = row[0]  #nombre
                year = int(row[1])  #año nacimiento
                covid = False
                if int(row[2]) == 1:  #covid:0 o 1
                    covid = True
                vaccine = int(row[3])  #número de dosis
                try:
                    appointment = row[4]
                    if checkFormatHour(appointment) == False:
                        #print(appointment, ' is not a right time (hh:minute)')
                        appointment = None

                except:
                    appointment = None

                objPatient = Patient(name, year, covid, vaccine, appointment)
                #name is the key, and objPatient the eleme
                if orderByName:
                    self.insert(name, objPatient)
                else:
                    if appointment:
                        self.insert(appointment, objPatient)
                    else:
                        print(
                            objPatient,
                            " was not added because appointment was not valid!!!"
                        )

            fichero.close()

    def searchPatients(self, year=2021, covid=None, vaccine=None):
        """return a new object of type HealthCenter 2 with the patients who
        satisfy the criteria of the search (parameters). 
        The function has to visit all patients, so the search must follow a level traverse of the tree.
        If you use a inorder traverse, the resulting tree should be a list!!!"""

        # Complexity O(nlogn)

        result = HealthCenter2()

        if self._root is None:
            print('tree is empty')
        else:

            q = queue.Queue()
            q.put(self._root)  # enqueue: we save the root

            while not (q.empty()):  # n
                current = q.get()  # dequeue
                if current.elem.year <= year and (
                        current.elem.covid == covid
                        or covid is None) and (current.elem.vaccine == vaccine
                                               or vaccine is None):
                    result.insert(current.elem.name,
                                  current.elem)  # log(n) function
                if current.left is not None:
                    q.put(
                        current.left
                    )  # enqueue the left element to check in the next iteration
                if current.right is not None:
                    q.put(
                        current.right
                    )  # enqueue the right element to check in the next iteration

        return result

    def vaccine(self, name, vaccinated):
        """This functions simulates the vaccination of a patient whose
        name is name. It returns True is the patient is vaccinated and False eoc"""
        node = self.find(name)  # save the patient; found by their key (name)
        if node is None:
            print(
                "{} does not exist in the calling health center".format(name))
            return False
        elif node.elem.vaccine == 2:
            print("{} has already received two vaccines".format(name))
            self.remove(
                name
            )  # patient is fully vaccinated so, eliminate it from HealthCenter
            newPat = Patient(name, node.elem.year, node.elem.covid, 2)
            vaccinated.insert(
                name, newPat)  # and add it to the vaccinated health center
            return False
        elif node.elem.vaccine == 1:
            self.remove(
                name)  # after vaccinated, the patient would have the 2 doses
            newPat = Patient(name, node.elem.year, node.elem.covid, 2)
            vaccinated.insert(
                name, newPat)  # so add them to the vaccinated health center
            return True
        else:
            #IMPOIRTANT: Clarify if the patient can recieve both doses at once
            node.elem.vaccine = 1
            return True

    def makeAppointment(self, name, time, schedule):
        """This functions makes an appointment 
        for the patient whose name is name. It functions returns True is the appointment 
        is created and False eoc """
        # Look for the patient in the calling Health Center
        node = self.find(name)

        # We first check the error cases (no patient and already vaccinated patient)
        if node is None:
            print(
                "{} does not exist in the calling health center".format(name))
            return False
        elif node.elem.vaccine == 2:
            print("{} has already received two vaccines".format(name))
            return False
        else:
            if checkFormatHour(time) is False:  # Check the format (hh:mm)
                print("Time format is not correct. Format: hh:mm")
                return False
            if schedule._root is None:
                node.elem.setAppointment(
                    time)  # Change time in calling health center
                schedule.insert(time, node.elem)  # Add it to the schedule BST
                return True
            elif schedule.search(
                    time
            ) is False:  # The slot is free, so assign it to the patient requesting it
                node.elem.setAppointment(
                    time)  # Change time in calling health center
                schedule.insert(time, node.elem)  # Add it to the schedule BST
                return True
            else:
                # The total number of possible time slots is 144, we check whether they are all occupied
                if schedule.size() == NUM_APPOINTMENTS:
                    print(
                        "{} cannot be appointed for a vaccine since there are no time slots"
                        .format(name))
                    return False
                else:
                    print(
                        "ALREDAY SOMEONE WITH TIME SLOT {}, LOOKING FOR A BEST FIT"
                        .format(time))

                    # Transform the time variable from string to integer

                    data = time.split(":")
                    hour = int(data[0])
                    minutes = int(data[1])

                    # Boolean variables to control if we have to look before or after
                    searchAfter = True
                    searchBefore = True

                    # Modify the variables to find the previous and next slot
                    # taking into account the hour and minutes format

                    if (minutes - 5) < 0:
                        prevTime = "{:02d}:{:02d}".format(hour - 1, 55)
                    else:
                        prevTime = "{:02d}:{:02d}".format(hour, minutes - 5)
                    if (minutes + 5) > 55:
                        nextTime = "{:02d}:{:02d}".format(hour + 1, 0)
                    else:
                        nextTime = "{:02d}:{:02d}".format(hour, minutes + 5)

                    while searchAfter or searchBefore:  # Loop until we get to the extremes #n
                        if checkFormatHour(
                                prevTime
                        ) is False:  # Check if previous time is not 08:00
                            searchBefore = False
                        if checkFormatHour(
                                nextTime
                        ) is False:  # Check if next time is not 20:00
                            searchAfter = False

                        # First we look if the previous slot is available
                        if searchBefore:
                            if schedule.search(prevTime) is False:  #log(n)
                                node.elem.setAppointment(prevTime)
                                schedule.insert(
                                    prevTime,
                                    node.elem)  # add it to the schedule BST
                                print(
                                    "Created appointment for {} at {}".format(
                                        name, prevTime))
                                return True
                            else:
                                # Update to seek the previous time slot
                                data = prevTime.split(":")
                                hour = int(data[0])
                                minutes = int(data[1])
                                if (minutes - 5) < 0:
                                    prevTime = "{:02d}:{:02d}".format(
                                        hour - 1, 55)
                                else:
                                    prevTime = "{:02d}:{:02d}".format(
                                        hour, minutes - 5)
                        # Look in the time slot afterwards
                        if searchAfter:
                            if schedule.search(nextTime) is False:
                                node.elem.setAppointment(nextTime)
                                schedule.insert(
                                    nextTime,
                                    node.elem)  # add it to the schedule BST
                                print(
                                    "Created appointment for {} at {}".format(
                                        name, nextTime))
                                return True
                            else:
                                data = nextTime.split(":")
                                hour = int(data[0])
                                minutes = int(data[1])
                                if (minutes + 5) > 55:
                                    nextTime = "{:02d}:{:02d}".format(
                                        hour + 1, 0)
                                else:
                                    nextTime = "{:02d}:{:02d}".format(
                                        hour, minutes + 5)


if __name__ == '__main__':

    ###Testing the constructor. Creating a health center where patients are sorted by name
    o = HealthCenter2('data/LosFrailes2.tsv')
    o.draw()
    print()

    print(
        'Patients who were born in or before than 1990, had covid and did not get any vaccine'
    )
    result = o.searchPatients(1990, True, 0)
    result.draw()
    print()

    print(
        'Patients who were born in or before than 1990, did not have covid and did not get any vaccine'
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

    ###Testing the constructor. Creating a health center where patients are sorted by name
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

    name = 'Ainoza'  #doest no exist
    result = o.vaccine(name, vaccinated)
    print("was patient vaccined?:", name, result)
    print('center:')
    o.draw(False)
    print('vaccinated:')
    vaccinated.draw(False)

    name = 'Abad'  #0 dosages
    result = o.vaccine(name, vaccinated)
    print("was patient vaccined?:", name, result)
    print('center:')
    o.draw(False)
    print('vaccinated:')
    vaccinated.draw(False)

    name = 'Font'  #with one dosage
    result = o.vaccine(name, vaccinated)
    print("was patient vaccined?:", name, result)
    print('center:')
    o.draw(False)
    print('vaccinated:')
    vaccinated.draw(False)

    name = 'Omar'  #with two dosage
    result = o.vaccine(name, vaccinated)
    print("was patient vaccined?:", name, result)
    print('center:')
    o.draw(False)
    print('vaccinated:')
    vaccinated.draw(False)
