# settings.py
# This is the settings window for AngerList.

import configparser
import datetime
import os

from PyQt5 import QtWidgets, QtGui
from PyQt5.Qt import Qt

import globalz
from common import getMainWindow


class Settings(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        # Disable the "?" button
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        # Initialize tabs
        self.tabs = QtWidgets.QTabWidget(self)
        self.tabs.addTab(GeneralSettings(self.tabs), 'General Settings')
        self.tabs.addTab(ArtistBlacklist(self.tabs), 'Artist Blacklist')
        self.tabs.addTab(PluginSettings(self.tabs), 'Plugins')

        # Add widget to layout
        L = QtWidgets.QGridLayout(self)
        L.addWidget(self.tabs)

        # Prevent changing window size
        L.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        # Update window name
        self.setWindowTitle('Settings')

    def closeEvent(self, e: QtGui.QCloseEvent):
        # Get main window
        mw = getMainWindow(self)

        # Check if scanner is running, prevent closing if so
        if mw.thread and mw.thread.isRunning():
            QtWidgets.QMessageBox.warning(self, 'AngerList On Air!', 'You can\'t interrupt AngerList while he\'s live. Please wait for the task to finish first.')
            e.ignore()

        # Otherwise save settings and close
        else:
            # Save general settings
            i = self.tabs.widget(0).maxdays.value()
            mw.config['General']['lastuse'] = str(datetime.date.today() - datetime.timedelta(days=i - 1))

            # Save artist blacklist
            tree = self.tabs.widget(1).tree
            mw.config['Blacklist']['blacklist'] = ','.join([tree.item(i).text() for i in range(tree.count())])

            # Save plugins - use the modulelist this time
            modulelist = getMainWindow(self).modulelist
            tree = self.tabs.widget(2).pluglist
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
            mw.printline('Settings updated!')

            # Call original function
            super().closeEvent(e)


class GeneralSettings(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Max days option
        self.maxdays = QtWidgets.QSpinBox(self)

        # Set suffix and special value
        self.maxdays.setSuffix(' days')
        self.maxdays.setSpecialValueText('day')

        # Limit value between 1 and 7 days
        self.maxdays.setRange(1, 7)

        # Set initial value
        currdate = datetime.date.today()
        olddate = datetime.datetime.strptime(getMainWindow(self).config['General']['lastuse'], "%Y-%m-%d").date()
        self.maxdays.setValue((currdate - olddate).days + 1)

        # Add elements to layout
        L = QtWidgets.QFormLayout(self)
        L.addRow('Get releases from the last', self.maxdays)


class ArtistBlacklist(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Create list widget
        self.tree = QtWidgets.QListWidget(self)

        # Allow editing list items by selecting and clicking
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)

        # Get the artist list and sort it
        blacklist = [i for i in getMainWindow(self).config['Blacklist']['blacklist'].split(',') if i.strip()]
        blacklist.sort()

        # Add the artists to the tree
        for artist in blacklist:
            newitem = QtWidgets.QListWidgetItem(artist, self.tree)
            newitem.setFlags(newitem.flags() | Qt.ItemIsEditable)

        # Events
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

        # Setup layout
        L = QtWidgets.QGridLayout(self)
        L.addWidget(self.tree, 0, 0, 1, 2)
        L.addWidget(self.addButton, 1, 0)
        L.addWidget(self.removeButton, 1, 1)

    def updateButtonStatus(self, currItem):
        # Set "Remove" button if any button is selected
        self.removeButton.setEnabled(bool(currItem))

        # If so, save its name for possible renaming purposes
        if currItem:
            self.backupText = currItem.text().strip()

    def updateItem(self, item: QtWidgets.QListWidgetItem):
        # Get the current item's text
        text = item.text().strip()

        # Check if text has changed
        if text != self.backupText:

            # If text is empty, restore it
            if not text:
                item.setText(self.backupText)

            # Otherwise set the new backup text and sort the list
            else:
                self.backupText = item.text()
                self.tree.sortItems(Qt.AscendingOrder)

    def addArtist(self):
        # Create new item
        newitem = QtWidgets.QListWidgetItem('New Artist', self.tree)

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

        # Version label
        self.version = QtWidgets.QLabel(self)
        self.version.setTextFormat(Qt.RichText)
        self.version.setAlignment(Qt.AlignRight)

        # Description label
        self.desc = QtWidgets.QLabel(self)
        self.desc.setWordWrap(True)
        self.desc.setTextFormat(Qt.RichText)

        # Plugin list
        self.pluglist = QtWidgets.QTreeWidget(self)
        self.pluglist.setHeaderHidden(True)
        self.pluglist.currentItemChanged.connect(self.updatePluginDesc)

        # Refresh Button
        self.refreshButton = QtWidgets.QPushButton('Rescan', self)
        self.refreshButton.clicked.connect(self.rescan)

        # Make a layout and set it
        lyt = QtWidgets.QGridLayout(self)
        lyt.addWidget(self.refreshButton, 0, 0, 1, 2)
        lyt.addWidget(self.pluglist, 1, 0, 1, 2)
        lyt.addWidget(self.author, 2, 0)
        lyt.addWidget(self.version, 2, 1)
        lyt.addWidget(self.desc, 3, 0, 1, 2)

        self.fillTree()

    def fillTree(self):
        # Grab the module list
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
        # Clear labels if no item is selected
        if not currItem:
            self.author.clear()
            self.version.clear()
            self.desc.clear()
            return

        # Set new texts only if the referenced plugin is different
        elif not (prevItem and currItem.data(0, Qt.UserRole) == prevItem.data(0, Qt.UserRole)):
            plugin = getMainWindow(self).modulelist[currItem.data(0, Qt.UserRole)]
            self.author.setText(f"<b>Author:</b>\n{plugin.author if plugin.author else '<i>Unknown</i>'}")
            self.version.setText(f"<b>Version:</b>\n{plugin.version if plugin.version else '<i>Unknown</i>'}")
            self.desc.setText(f"<b>Description:</b>\n{plugin.description if plugin.description else '<i>No description provided.</i>'}")

    def rescan(self):
        # Clear the tree - metadata will clear itself automatically
        self.pluglist.clear()

        # Get main window
        mw = getMainWindow(self)

        # Clear the module list
        mw.modulelist.clear()

        # Disable the rescan button
        self.refreshButton.setEnabled(False)

        # Run the scanner again
        mw.runThread(True)

        # Refill the tree and re-enable the button when the thread finishes
        mw.thread.finished.connect(self.fillTree)
        mw.thread.finished.connect(lambda: self.refreshButton.setEnabled(True))


def readconfig(config: configparser.ConfigParser):
    # Preload max previous date
    date2 = datetime.date.today() - datetime.timedelta(days=6)

    # Placeholders for eventual missing values
    config['General'] = {'lastuse': str(date2)}
    config['Blacklist'] = {'blacklist': ''}
    config['Plugins'] = {}

    # If the file exists, override the values by reading the file
    if os.path.isfile(globalz.configfile):
        config.read(globalz.configfile)

    # Check that the last usage date is not more than a week ago. If so, set it to a week ago
    date = datetime.datetime.strptime(config['General']['lastuse'], "%Y-%m-%d").date()
    config['General']['lastuse'] = str(max(date, date2))


def writeconfig(config: configparser.ConfigParser, modulelist: dict):
    # Set date to today
    config['General']['lastuse'] = str(datetime.date.today())

    # Remove blacklist section if empty
    if not config['Blacklist']['blacklist']:
        config.remove_section('Blacklist')

    # Write plugins or remove section if empty
    if modulelist:
        for module, moduledata in modulelist.items():
            config['Plugins'][module] = 'yes' if moduledata.enabled else 'no'
            for genre, genrestatus in moduledata.genres.items():
                config['Plugins'][f'{module}_{genre}'] = 'yes' if genrestatus else 'no'
    else:
        config.remove_section('Plugins')

    # Remove any other unknown section
    for section in reversed(config.sections()):
        if section not in ['General', 'Plugins', 'Blacklist']:
            config.remove_section(section)

    # Write to file
    with open(globalz.configfile, 'w') as f:
        config.write(f)
