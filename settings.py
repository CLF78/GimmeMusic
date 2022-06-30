#!/usr/bin/env python3

# settings.py
# This file defines GimmeMusic's settings window.

import importlib

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt

import globalz
from common import getMainWindow, printline


class Settings(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        # Disable the "?" button
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        # Initialize tabs
        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.addTab(GeneralSettings(self.tabs), 'General')
        self.tabs.addTab(PluginSettings(self.tabs), 'Plugins')

        # Add widget to layout
        L = QtWidgets.QVBoxLayout(self)
        L.addWidget(self.tabs)

        # Update window name
        self.setWindowTitle('Settings')

    def closeEvent(self, e: QtGui.QCloseEvent):
        """
        Overrides the close event to save the settings to the config.
        """
        mw = getMainWindow(self)

        # Check if the scanner is running, prevent closing if so
        if mw.thread and mw.thread.isRunning():
            QtWidgets.QMessageBox.warning(self, 'Scanner Running!', 'Please wait for the scan to finish first.')
            e.ignore()
        else:
            # Save lastuse
            i = self.tabs.widget(0).maxdays.value()
            globalz.lastuse = QtCore.QDate.currentDate().addDays(-i - 1)

            # Save artist blacklist
            tree = self.tabs.widget(0).tree
            mw.config.setValue('Blacklist/blacklist', ','.join([tree.item(i).text() for i in range(tree.count())]))

            # Save plugins - use the modulelist this time
            modulelist = mw.modulelist
            tree = self.tabs.widget(1).pluglist
            for i in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(i)
                pluginName = item.data(0, Qt.UserRole)
                modulelist[pluginName].enabled = bool(item.checkState(0))

                # Save the children!
                for j in range(item.childCount()):
                    child = item.child(j)
                    childName = child.text(0)[len(item.text(0)) + 3:].lower()
                    modulelist[pluginName].genres[childName] = bool(child.checkState(0))

            # Flaunt our success
            printline(self, 'Settings updated!')

            # Call original function
            super().closeEvent(e)


class GeneralSettings(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        ###################
        # Max Days Option #
        ###################
        self.maxdays = QtWidgets.QSpinBox(self)

        # Set suffix and special value
        self.maxdays.setSuffix(' days')
        self.maxdays.setSpecialValueText('day')

        # Limit value between 1 and 7 days
        self.maxdays.setRange(1, 7)

        # Set initial value
        currdate = QtCore.QDate.currentDate()
        olddate = globalz.lastuse
        self.maxdays.setValue(olddate.daysTo(currdate) + 1)

        ####################
        # Artist Blacklist #
        ####################
        self.tree = QtWidgets.QListWidget(self)

        # Allow editing list items by selecting and clicking
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)

        # Get the artist list, discarding whitespace and removing duplicates
        blacklist = getMainWindow(self).config.value('Blacklist/blacklist', '').split(',')
        #blacklist = set(filter(None, map(lambda i: i.strip(), blacklist)))

        # Fill the tree
        for artist in blacklist:
            newitem = QtWidgets.QListWidgetItem(artist, self.tree)
            newitem.setFlags(newitem.flags() | Qt.ItemIsEditable)

        # Sort it
        self.tree.sortItems(0)

        # Set up events
        self.tree.itemChanged.connect(self.updateItem)
        self.tree.currentItemChanged.connect(self.updateButtonStatus)

        # Remove button
        self.removeButton = QtWidgets.QPushButton('Remove Selected', self)
        self.removeButton.setEnabled(False)
        self.removeButton.clicked.connect(lambda: self.tree.takeItem(self.tree.row(self.tree.currentItem())))

        # Add button
        self.addButton = QtWidgets.QPushButton('Add Entry', self)
        self.addButton.clicked.connect(self.addArtist)

        # Backup text
        self.backupText = ''

        ################
        # Layout Setup #
        ################

        # Create a grid layout
        L = QtWidgets.QGridLayout(self)

        # Add a label
        L.addWidget(QtWidgets.QLabel('General Settings:', self), 0, 0, 1, 2)

        # Enclose the lastuse setting in a frame
        frame = QtWidgets.QFrame(self)
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)

        # Add the lastuse setting to a form layout
        form = QtWidgets.QFormLayout(frame)
        form.addRow('Get releases from the last:', self.maxdays)

        # Add the frame to the grid layout
        L.addWidget(frame, 1, 0, 1, 2)

        # Add 16 pixels padding so it doesn't look awful
        L.addItem(QtWidgets.QSpacerItem(0, 16), 2, 0, 1, 2)

        # Add the artist blacklist
        L.addWidget(QtWidgets.QLabel('Artist Blacklist:', self), 3, 0, 1, 2)
        L.addWidget(self.tree, 4, 0, 1, 2)
        L.addWidget(self.addButton, 5, 0)
        L.addWidget(self.removeButton, 5, 1)

    def updateButtonStatus(self, currItem):
        """
        Disables the remove button if no artist is selected and backs up the text for failed renames.
        """
        self.removeButton.setEnabled(bool(currItem))
        if currItem:
            self.backupText = currItem.text().strip()

    def updateItem(self, item: QtWidgets.QListWidgetItem):
        """
        Restores the artist's name if the new name is empty, else sorts the list again.
        """
        text = item.text().strip()

        # Check if text has changed
        if text != self.backupText:

            # If text is empty, restore it
            if not text:
                item.setText(self.backupText)

            # Otherwise set the new backup text and sort the list
            else:
                self.backupText = text
                self.tree.sortItems(0)

    def addArtist(self):
        """
        Adds a new artist to the blacklist.
        """
        newitem = QtWidgets.QListWidgetItem('New Entry', self.tree)

        # Set it as editable
        newitem.setFlags(newitem.flags() | Qt.ItemIsEditable)

        # Set it as current item to trigger the updateItem function and save the change
        self.tree.setCurrentItem(newitem)

        # Start editing it
        self.tree.editItem(newitem)


class PluginSettings(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Author label
        self.author = QtWidgets.QLabel(self)
        self.author.setTextFormat(Qt.RichText)
        self.author.setHidden(True)

        # Version label
        self.version = QtWidgets.QLabel(self)
        self.version.setTextFormat(Qt.RichText)
        self.version.setAlignment(Qt.AlignRight)
        self.version.setHidden(True)

        # Description label
        self.desc = QtWidgets.QLabel(self)
        self.desc.setWordWrap(True)
        self.desc.setTextFormat(Qt.RichText)
        self.desc.setHidden(True)

        # Plugin list
        self.pluglist = QtWidgets.QTreeWidget(self)
        self.pluglist.setHeaderHidden(True)
        self.pluglist.currentItemChanged.connect(self.updatePluginDesc)

        # Refresh Button
        self.refreshButton = QtWidgets.QPushButton('Refresh', self)
        self.refreshButton.clicked.connect(self.rescan)

        # Make a layout and set it
        lyt = QtWidgets.QGridLayout(self)
        lyt.addWidget(self.refreshButton, 0, 0, 1, 2)
        lyt.addWidget(self.pluglist, 1, 0, 1, 2)
        lyt.addWidget(self.author, 2, 0)
        lyt.addWidget(self.version, 2, 1)
        lyt.addWidget(self.desc, 3, 0, 1, 2)

        # Fill the tree
        self.fillTree()

    def fillTree(self):
        """
        Takes the module list and fills the tree based on its contents.
        """
        modulelist = getMainWindow(self).modulelist
        for modname, module in modulelist.items():

            # Create item
            newitem = QtWidgets.QTreeWidgetItem(self.pluglist, [module.name])

            # Set reference to module name
            newitem.setData(0, Qt.UserRole, modname)

            # If it has genres, set auto tristate and create children
            if module.genres:
                newitem.setFlags(newitem.flags() | Qt.ItemIsAutoTristate)
                for genre, enabled in module.genres.items():
                    newChild = QtWidgets.QTreeWidgetItem(newitem, [f'{module.name} - {genre.title()}'])
                    newChild.setCheckState(0, enabled * 2)
                    newChild.setData(0, Qt.UserRole, modname)

            # Else just set the check
            else:
                newitem.setCheckState(0, module.enabled * 2)

        # Sort the tree
        self.pluglist.sortItems(0, Qt.AscendingOrder)

    def updatePluginDesc(self, currItem, prevItem):
        """
        Shows/hides the author/version/description labels and updates their texts.
        """
        self.author.setHidden(not currItem)
        self.version.setHidden(not currItem)
        self.desc.setHidden(not currItem)

        # Set new texts only if the referenced plugin is different
        if currItem and not (prevItem and currItem.data(0, Qt.UserRole) == prevItem.data(0, Qt.UserRole)):
            plugin = getMainWindow(self).modulelist[currItem.data(0, Qt.UserRole)]
            self.author.setText(f"<b>Author:</b>\n{plugin.author if plugin.author else '<i>N/A</i>'}")
            self.version.setText(f"<b>Version:</b>\n{plugin.version if plugin.version else '<i>N/A</i>'}")
            self.desc.setText(f"<b>Description:</b>\n{plugin.description if plugin.description else '<i>No description provided.</i>'}")

    def rescan(self):
        """
        Clears the plugin list and triggers a rescan.
        """
        self.pluglist.clear()

        # Get main window
        mw = getMainWindow(self)

        # Clear the module list
        mw.modulelist.clear()

        # Disable the rescan button
        self.refreshButton.setEnabled(False)

        # Invalidate cache to account for plugins being added during execution
        importlib.invalidate_caches()

        # Run the scanner again
        mw.runThread(True)

        # Refill the tree and re-enable the button when the thread finishes
        mw.thread.finished.connect(self.fillTree)
        mw.thread.finished.connect(lambda: self.refreshButton.setEnabled(True))


def readconfig(config: QtCore.QSettings):
    """
    Initializes the lastuse variable.
    """
    # Check that the last usage date is not more than a week ago. If so, set it to a week ago
    minDate = QtCore.QDate.currentDate().addDays(-6)

    # Make sure the date is valid by catching exceptions
    newDate = config.value('General/lastuse', minDate)
    newDate = max(newDate, minDate)

    # Store it
    globalz.lastuse = newDate


def writeconfig(config: QtCore.QSettings, modulelist: dict, mwgeometry: QtCore.QByteArray, mwstate: QtCore.QByteArray, splitterstate: QtCore.QByteArray):
    """
    Writes the settings to an .ini file.
    """
    # Set date to today
    config.setValue('General/lastuse', QtCore.QDate.currentDate())

    # Remove blacklist section if empty
    if not config.value('Blacklist/blacklist', []):
        config.remove('Blacklist')

    # Set plugins or remove section if empty
    if modulelist:
        for module, moduledata in modulelist.items():
            config.setValue(f'Plugins/{module}', moduledata.enabled)
            for genre, genrestatus in moduledata.genres.items():
                config.setValue(f'Plugins/{module}_{genre}', genrestatus)
    else:
        config.remove('Plugins')

    # Set window settings
    config.setValue('WindowSettings/mwgeometry', mwgeometry)
    config.setValue('WindowSettings/mwstate', mwstate)
    config.setValue('WindowSettings/splitterstate', splitterstate)

    # Remove any other unknown section
    for section in config.allKeys():
        if not section.startswith(('General', 'Plugins', 'Blacklist', 'WindowSettings')):
            config.remove(section)

    # Write to file
    config.sync()


if __name__ == '__main__':
    print("Run main.py to access the program!")
