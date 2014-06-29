#!/usr/bin/python -d
# -*- coding: UTF-8 -*-
__version__="3.0"
 
import sys
import os
from PyQt4 import QtCore, QtGui
import xml.etree.ElementTree as etree
import re
import textwrap
from fieldbookGui import Ui_Fieldbook
import images
from random import choice


class Orthographies:

    def toIPA(IPA):
        ortho = myapp.ui.dataIndex.root.attrib.get('Orth')
        mapping = myapp.ui.dataIndex.root.findtext('Orthographies/Map[@Name="%s"]' %ortho)
        pairList = mapping.split('; ')
        for pair in pairList:
            segList = pair.split(',')
            segIn = segList[0]
            segOut= segList[1].replace(' ','')
            IPA = IPA.replace(segIn,segOut)
        return IPA

    def testTransform(IPA):
        mapping = myapp.ui.oOrder.toPlainText()
        pairList = mapping.split('; ')
        for pair in pairList:
            segList = pair.split(',')
            segIn = segList[0]
            segOut= segList[1].replace(' ','')
            IPA = IPA.replace(segIn,segOut)
        return IPA
    
class idGenerator:
    '''generates unique id numbers for various types of elements'''
    
    def generateID(prefix, dictionary):
        codeList = sorted(dictionary.keys(), key=lambda i : int(i[2:]))
        topCode = int(codeList[-1][2:] )
        topCode += 1
        newID = prefix + str(topCode)
        while newID in codeList:
            topCode += 1
            newID = prefix + str(topCode)
        return newID

class cardLoader:
    
    #####LOAD CARDS####

    def loadDataCard(Fieldbook,dataRoot,navBtn=False):
        Fieldbook.ui.dataIndex.currentCard = dataRoot.attrib.get('DsetID')
        Fieldbook.ui.dataIndex.lastDset = dataRoot.attrib.get('DsetID')   
        Fieldbook.ui.dataIndex.root.set('LastDset',Fieldbook.ui.dataIndex.lastDset)
        if navBtn == False:
            Fieldbook.ui.tCardStack.addToQueue(Fieldbook,Fieldbook.ui.dataIndex.currentCard)
        
        Fieldbook.ui.dSource.clear()
        entry = dataRoot.attrib.get('Spkr')
        if entry:
          Fieldbook.ui.dSource.setPlainText(entry)
          
        Fieldbook.ui.dResearcher.clear()
        entry = dataRoot.attrib.get('Rschr')
        if entry:
          Fieldbook.ui.dResearcher.setPlainText(entry)
          
        Fieldbook.ui.dDate.clear()
        entry = dataRoot.attrib.get('Date')
        if entry:
          Fieldbook.ui.dDate.setPlainText(entry)
          
        Fieldbook.ui.dUpdated.clear()
        entry = dataRoot.attrib.get('Update')
        if entry:
          Fieldbook.ui.dUpdated.setPlainText(entry)
          
        Fieldbook.ui.dKeywords.clear()
        entry = dataRoot.attrib.get('Kywd')
        if entry:
          Fieldbook.ui.dKeywords.setPlainText(entry)
          
        Fieldbook.ui.dNotes.clear()
        entry = dataRoot.findtext('Comments')
        if entry:
          entry = entry.replace('{Italics}','<i>')
          entry = entry.replace('{/Italics}','</i>')
          entry = entry.replace('{{','<')
          entry = entry.replace('}}','>')
          Fieldbook.ui.dNotes.setText(entry)
          
        Fieldbook.ui.dTitle.clear()
        entry = dataRoot.findtext('Title')
        if entry:
          entry = entry.replace('{Italics}','<i>')
          entry = entry.replace('{/Italics}','</i>')
          entry = entry.replace('{{','<')
          entry = entry.replace('}}','>')
          Fieldbook.ui.dTitle.setText(entry)
          
        Fieldbook.ui.dData.clear()
        entry = dataRoot.findtext('Data')
        if entry:
          entry = entry.replace('{Italics}','<i>')
          entry = entry.replace('{/Italics}','</i>')
          entry = entry.replace('{{','<')
          entry = entry.replace('}}','>')
          Fieldbook.ui.dData.setText(entry)
          
        #Recordings
        Fieldbook.ui.dRecordings.clear()
        Fieldbook.ui.dSoundFileMeta.clear()
        media = dataRoot.findall('Sound')
        if media:
            for i in range(0,len(media)):
                mediaIndex = media[i].attrib.get('MediaRef')
                mediaElement = Fieldbook.ui.dataIndex.mediaDict[mediaIndex]
                recording = os.path.basename(fullPath)
                speaker = mediaElement.attrib.get('Spkr')
                date = mediaElement.attrib.get('Date')
                Fieldbook.ui.dRecordings.insertItem(i, recording)
                Fieldbook.ui.dRecordings.setItemData(i, mediaIndex,35)
                label = Fieldbook.ui.dSoundFileMeta
                cardLoader.setMetaLabel(label,speaker,date)
        Fieldbook.ui.dRecordings.setCurrentIndex(0)

    def textTableBuilder(node, eg, j = 0):
        '''builds tables for presenting lines on the text card'''
        aFlag = 1
        entryRow0 = node.findtext('Line')
        entryRow0 = entryRow0.replace('{Italics}','<i>')
        entryRow0 = entryRow0.replace('{/Italics}','</i>')
        entryRow0 = entryRow0.replace('{{','<')
        entryRow0 = entryRow0.replace('}}','>')
        try: 
            entryRow1 = node.findtext('Mrph').split('\t')
            entryRow2 = node.findtext('ILEG').split('\t')
        except AttributeError:
            aFlag = 0
        if len(node.findtext('L1Gloss')) == 0:
            entryRow3 = node.findtext('L2Gloss')
        else:
            entryRow3 = node.findtext('L1Gloss')
        entryRow3 = entryRow3.replace('{Italics}','<i>')
        entryRow3 = entryRow3.replace('{/Italics}','</i>')
        entryRow3 = entryRow3.replace('{{','<')
        entryRow3 = entryRow3.replace('}}','>')
        #need to allow for L2 if desired
        newTable = textTable(parent=None)
        if aFlag ==1:
            newTable.setRowCount(4)
            newTable.setColumnCount(len(entryRow1)+1)
            newTable.setRowHeight(0,20)
            newTable.setRowHeight(1,20)          
            newTable.setRowHeight(2,20)
            newTable.setRowHeight(3,20)
        else:
            newTable.setRowCount(2)
            newTable.setColumnCount(2)
            newTable.setRowHeight(0,20)
            newTable.setRowHeight(1,20)
            newTable.setMinimumHeight(48)
        tableCellNumber = QtGui.QTableWidgetItem(1001)
        tableCellNumber.setText(str(j+1))
        tableCellNumber.setData(35,node)
        tableCellNumber.setFlags(QtCore.Qt.ItemIsEnabled)
        tableCellLine = QtGui.QTableWidgetItem(10001)
        tableCellLine.setText(entryRow0)
        tableCellGloss = QtGui.QTableWidgetItem(10001)
        tableCellGloss.setText(entryRow3)
        tableCellInert = QtGui.QTableWidgetItem(1001)
        tableCellInert.setFlags(QtCore.Qt.ItemIsEnabled)
        tableCellInert2 = QtGui.QTableWidgetItem(1001)
        tableCellInert2.setFlags(QtCore.Qt.ItemIsEnabled)
        tableCellInert3 = QtGui.QTableWidgetItem(1001)
        tableCellInert3.setFlags(QtCore.Qt.ItemIsEnabled)
        if aFlag == 1:
            newTable.setItem(3,len(entryRow1),tableCellGloss)
            newTable.resizeColumnToContents(len(entryRow1))
            newTable.takeItem(3,len(entryRow1))
            for i in range(1,len(entryRow1)+1):
                parse = entryRow2[i-1].replace('{ABB}','<small>')
                parse = parse.replace('{/ABB}','</small>')
                parse = parse.replace('{{/ABB}}','</small>')
                parse = parse.replace('{{ABB}}','<small>')
                parse = parse.replace('{{','<')
                parse = parse.replace('}}','>')
                tableCellTop = QtGui.QTableWidgetItem(10001)
                tableCellTop.setText(entryRow1[i-1])
                tableCellBottom = QtGui.QTableWidgetItem(10001)
                tableCellBottom.setText(parse + " ")
                tableCellBottom.setTextAlignment(QtCore.Qt.AlignBottom)
                newTable.setItem(1,i,tableCellTop)
                newTable.setItem(2,i,tableCellBottom)
                if i != len(entryRow1):
                    newTable.resizeColumnToContents(i)
        newTable.setItem(0,0,tableCellNumber)
        newTable.resizeColumnToContents(0)
        if aFlag == 1:
            newTable.setItem(0,1,tableCellLine)
            newTable.setItem(3,1,tableCellGloss)
            newTable.setSpan(0,1,1,len(entryRow1))
            newTable.setSpan(3,1,1,len(entryRow1))
            newTable.setItem(1,0,tableCellInert)
            newTable.setItem(2,0,tableCellInert2)
            newTable.setItem(3,0,tableCellInert3)
        else:
            newTable.setItem(0,1,tableCellLine)
            newTable.setItem(1,1,tableCellGloss)
            newTable.setItem(1,0,tableCellInert)
        newTable.setObjectName(eg)
        newTable.adjustSize()
        newTable.setToolTip(QtGui.QApplication.translate("Fieldbook",
                                                         "click on line number to view \n"
                                                         "example in the Examples tab.",
                                                         None, QtGui.QApplication.UnicodeUTF8))
        return newTable

    def loadTextCard(Fieldbook, textRoot, navBtn=False):       
        Fieldbook.ui.dataIndex.currentCard = textRoot.attrib.get('TextID')   
        Fieldbook.ui.dataIndex.lastText = textRoot.attrib.get('TextID')
        Fieldbook.ui.dataIndex.root.set('LastText',Fieldbook.ui.dataIndex.lastText)
        if navBtn == False:
            Fieldbook.ui.tCardStack.addToQueue(Fieldbook,Fieldbook.ui.dataIndex.currentCard)
        Fieldbook.ui.tSource.clear()
        entry = textRoot.attrib.get('Spkr')
        if entry:
            Fieldbook.ui.tSource.setPlainText(entry)         
        Fieldbook.ui.tResearcher.clear()
        entry = textRoot.attrib.get('Rschr')
        if entry:
            Fieldbook.ui.tResearcher.setPlainText(entry)         
        Fieldbook.ui.tDate.clear()
        entry = textRoot.attrib.get('Date')
        if entry:
            Fieldbook.ui.tDate.setPlainText(entry)          
        Fieldbook.ui.tUpdated.clear()
        entry = textRoot.attrib.get('Update')
        if entry:
            Fieldbook.ui.tUpdated.setPlainText(entry)
        Fieldbook.ui.tTranscriber.clear()
        entry = textRoot.attrib.get('Trns')
        if entry:
            Fieldbook.ui.tTranscriber.setPlainText(entry)         
        Fieldbook.ui.tTitle.clear()
        entry = textRoot.findtext('Title')
        if entry:
            entry = entry.replace('{Italics}','<i>')
            entry = entry.replace('{/Italics}','</i>')
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            Fieldbook.ui.tTitle.setText(entry) 
        Fieldbook.ui.tNotes.clear()
        entry = textRoot.findtext('Comments')
        if entry:
            entry = entry.replace('{Italics}','<i>')
            entry = entry.replace('{/Italics}','</i>')
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            Fieldbook.ui.tNotes.setText(entry)         
        numLines = len(textRoot.findall('Ln'))
        progDialog = QtGui.QProgressDialog("Loading text ...", "Stop", 0, numLines, parent=None)
        progDialog.setWindowModality(QtCore.Qt.WindowModal)
        progDialog.setWindowTitle('Loading')
        if Fieldbook.ui.tText.layout() != None:
            while (Fieldbook.ui.tText.layout().takeAt(0)) != None:
                Fieldbook.ui.tText.layout().takeAt(0)
            textLayout = Fieldbook.ui.tText.layout()
        else:
            textLayout = QtGui.QVBoxLayout()
        tableDict = {}
        j = 0
        for child in textRoot.iter('Ln'):
            eg = child.attrib.get('LnRef')
            progDialog.setValue(j)
            if (progDialog.wasCanceled()):
                break
            for node in Fieldbook.ui.dataIndex.root.iter('Ex'):
                if node.attrib.get('ExID') == eg:
                    newTable = cardLoader.textTableBuilder(node, eg, j)
                    tableDict[j] = newTable
                    j = j + 1
                    break
        progDialog.setValue(numLines)
        for i in range(0,len(tableDict)):
            textLayout.addWidget(tableDict[i])
        Fieldbook.ui.tText.setLayout(textLayout)
        Fieldbook.ui.dataIndex.unsavedEdit = 0
          
        #Recordings
        Fieldbook.ui.tRecordings.clear()
        Fieldbook.ui.tSoundFileMeta.clear()
        media = textRoot.findall('Sound')
        if media:
            for i in range(0,len(media)):
                mediaIndex = media[i].attrib.get('MediaRef')
                mediaElement = Fieldbook.ui.dataIndex.mediaDict[mediaIndex]
                recording = os.path.basename(fullPath)
                speaker = mediaElement.attrib.get('Spkr')
                date = mediaElement.attrib.get('Date')
                Fieldbook.ui.tRecordings.insertItem(i, recording)
                Fieldbook.ui.tRecordings.setItemData(i, mediaIndex,35)
                Fieldbook.ui.tSoundFileMeta.setText(speaker + " " + date)
            Fieldbook.ui.tRecordings.setCurrentIndex(0)
            label = Fieldbook.ui.tSoundFileMeta
            cardLoader.setMetaLabel(label,speaker,date)
            Fieldbook.ui.tRecordings.setEnabled(1)
            Fieldbook.ui.tDelEgBtn.setEnabled(1)          
        else:
            Fieldbook.ui.tRecordings.setEnabled(0)
            Fieldbook.ui.tDelEgBtn.setEnabled(0)          
 
    def loadEgCard(Fieldbook, egRoot, navBtn=False):
        
        Fieldbook.ui.dataIndex.currentCard = egRoot.attrib.get('ExID')
        Fieldbook.ui.dataIndex.lastEG = egRoot.attrib.get('ExID')   
        Fieldbook.ui.dataIndex.root.set('LastEG',Fieldbook.ui.dataIndex.lastEG)
        if navBtn == False:
            Fieldbook.ui.tCardStack.addToQueue(Fieldbook,Fieldbook.ui.dataIndex.currentCard)

        Fieldbook.ui.eKeywords.clear()
        entry = egRoot.attrib.get('Kywd')
        if entry:
            Fieldbook.ui.eKeywords.setText(entry)

        Fieldbook.ui.eSourceText.clear()
        entry = egRoot.attrib.get('SourceText')
        if entry:
            try:
                textElement = Fieldbook.ui.dataIndex.textDict[entry]
                entry = textElement.findtext('Title')
                Fieldbook.ui.eSourceText.setPlainText(entry)
                lineList = textElement.findall('Ln')
                for i in range(0,len(lineList)-1):
                    if lineList[i].attrib.get('LnRef') == egRoot.attrib.get('ExID'):
                        Fieldbook.ui.eLineNumber.setPlainText('line ' + str(i + 1))
            except KeyError:
                pass
          
        Fieldbook.ui.eTimeCode.clear()
        entry = egRoot.attrib.get('Time')
        if entry:
            Fieldbook.ui.eTimeCode.setPlainText(entry)
          
        Fieldbook.ui.eSource.clear()
        entry = egRoot.attrib.get('Spkr')
        if entry:
            Fieldbook.ui.eSource.setPlainText(entry)
          
        Fieldbook.ui.eResearcher.clear()
        entry = egRoot.attrib.get('Rschr')
        if entry:
            Fieldbook.ui.eResearcher.setPlainText(entry)
          
        Fieldbook.ui.eDate.clear()
        entry = egRoot.attrib.get('Date')
        if entry:
            Fieldbook.ui.eDate.setPlainText(entry)
          
        Fieldbook.ui.eUpdated.clear()
        entry = egRoot.attrib.get('Update')
        if entry:
            Fieldbook.ui.eUpdated.setPlainText(entry)
          
        Fieldbook.ui.eLine.clear()
        entry = egRoot.findtext('Line')
        if entry:
            entry = entry.replace('{Italics}','<i>')
            entry = entry.replace('{/Italics}','</i>')
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            Fieldbook.ui.eLine.setText(entry)

        Fieldbook.ui.eL1Gloss.clear()
        entry = egRoot.findtext('L1Gloss')
        if entry:
            entry = entry.replace('{Italics}','<i>')
            entry = entry.replace('{/Italics}','</i>')
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            Fieldbook.ui.eL1Gloss.setText(entry)

        Fieldbook.ui.eL2Gloss.clear()
        entry = egRoot.findtext('L2Gloss')
        if entry:
            entry = entry.replace('{Italics}','<i>')
            entry = entry.replace('{/Italics}','</i>')
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            Fieldbook.ui.eL2Gloss.setText(entry)

        Fieldbook.ui.eAnalysis.clear()
        Fieldbook.ui.eAnalysis.setColumnCount(0)
        if egRoot.findtext('Mrph') != None:
            entryRow1 = egRoot.findtext('Mrph').split('\t')
            entryRow2 = egRoot.findtext('ILEG').split('\t')
            Fieldbook.ui.eAnalysis.setRowCount(2)
            Fieldbook.ui.eAnalysis.setColumnCount(len(entryRow1))
            Fieldbook.ui.eAnalysis.setRowHeight(0,20)
            Fieldbook.ui.eAnalysis.setRowHeight(1,20)
            for i in range(len(entryRow1)):
                parse = entryRow2[i].replace('{ABB}','<small>')
                parse = parse.replace('{/ABB}','</small>')
                parse = parse.replace('{{/ABB}}','</small>')
                parse = parse.replace('{{ABB}}','<small>')
                parse = parse.replace('{{','<')
                parse = parse.replace('}}','>')
                parse = parse.replace(' ','')
                tableCellTop = QtGui.QTableWidgetItem(10001)
                tableCellTop.setText(entryRow1[i])
                Fieldbook.ui.eAnalysis.setItem(0,i,tableCellTop)
                tableCellBottom = QtGui.QTableWidgetItem(10001)
                tableCellBottom.setText(parse + " ")
                tableCellBottom.setTextAlignment(QtCore.Qt.AlignBottom)
                Fieldbook.ui.eAnalysis.setItem(1,i,tableCellBottom)
                Fieldbook.ui.eAnalysis.resizeColumnToContents(i)
        lastColumn = Fieldbook.ui.eAnalysis.columnCount()
        Fieldbook.ui.eAnalysis.insertColumn(lastColumn)
        lastHeadWidget = QtGui.QTableWidgetItem(1001)
        lastHeadWidget.setText('+')
        Fieldbook.ui.eAnalysis.setHorizontalHeaderItem(lastColumn,lastHeadWidget)
        Fieldbook.ui.eAnalysis.resizeColumnToContents(lastColumn)
        
        for i in range(0,Fieldbook.ui.eAnalysis.rowCount()):
            inertWidget = QtGui.QTableWidgetItem(1001)
            inertWidget.setFlags(QtCore.Qt.NoItemFlags)
            Fieldbook.ui.eAnalysis.setItem(1,lastColumn,inertWidget)
            
        Fieldbook.ui.eNotes.clear()
        entry = egRoot.findtext('Comments')
        if entry:
            entry = entry.replace('{Italics}','<i>')
            entry = entry.replace('{/Italics}','</i>')
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            Fieldbook.ui.eNotes.setText(entry)
              
        #Recordings
        Fieldbook.ui.eRecordings.clear()
        Fieldbook.ui.eSoundFileMeta.clear()
        media = egRoot.findall('Sound')
        if media:
            for i in range(0,len(media)):
                mediaIndex = media[i].attrib.get('MediaRef')
                mediaElement = Fieldbook.ui.dataIndex.mediaDict[mediaIndex]
                recording = mediaElement.attrib.get('Filename')
                speaker = mediaElement.attrib.get('Spkr')
                date = mediaElement.attrib.get('Date')
                Fieldbook.ui.eRecordings.insertItem(i, recording)
                Fieldbook.ui.eRecordings.setItemData(i, mediaIndex,35)
            Fieldbook.ui.eRecordings.setCurrentIndex(0)
            Fieldbook.ui.eSoundFileMeta.setText(speaker + " " + date)
            Fieldbook.ui.eRecordings.setCurrentIndex(0)
            label = Fieldbook.ui.eSoundFileMeta
            cardLoader.setMetaLabel(label,speaker,date)
            Fieldbook.ui.eRecordings.setEnabled(1)
            Fieldbook.ui.eDelEgBtn.setEnabled(1)              
        else:
            Fieldbook.ui.eRecordings.setEnabled(0)
            Fieldbook.ui.eDelEgBtn.setEnabled(0)   
        Fieldbook.ui.eRecordings.setItemData(0, Fieldbook.ui.dataIndex.lastEG, 33)

    def breakLines(text, lineLength,indent=None):
        wrapper = textwrap.TextWrapper()
        if indent != None:
          wrapper.initial_indent = indent
          wrapper.subsequent_indent = indent
        wrapper.width = lineLength
        textList = wrapper.wrap(text)
        newText = ''
        newText = '<br />'.join(textList)
        return newText

    def loadDefinitions(lexRoot):
        myapp.ui.lL1Definition.clear()
        myapp.ui.lL2Definition.clear()
        subentry = lexRoot.findall('Def')
        L1DefList = []
        L2DefList = []
        for i in range(0,len(subentry)):
            #L1
            entry = ''
            dialect = ''
            variant = ''
            alternative = ''
            POS = subentry[i].findtext('POS')
            index = subentry[i].attrib.get('Index')
            if POS:
                entry = "(" + POS + ") "
            Reg = subentry[i].findtext('Reg')
            dNode = subentry[i].find('Dia')
            if dNode != None:
                dialect = dNode.attrib.get('Dialect')
                entry = entry + " <i>" + dialect + "</i> "
                aNodeList = dNode.findall('Alternative')
                if len(aNodeList) != 0:
                    crossRefList = []
                    altList = []
                    j = 0
                    for item in aNodeList:
                        variant = item.attrib.get('Variant')
                        crossref = item.attrib.get('CrossRef')
                        alternative = item.text
                        if j == 0 and j == len(aNodeList) - 1:
                            entry = entry + "[" + variant + " " + alternative + "] "
                        elif j == 0:
                            entry = entry + "[" + variant + " " + alternative
                        elif j == len(aNodeList) - 1:
                            entry = entry + "; " + variant + " " + alternative + "] "
                        else:
                            entry = entry + "; " + variant + " " + alternative
                        if crossref:
                            crossRefList.append(crossref)
                            altList.append(alternative)
                        if len(crossRefList) != 0:
                            field = 'lL1Definition'
                            cardLoader.buildContextMenu(field,crossRefList,altList)
                        j += 1
                      
            if Reg:
                entry = entry + "<i>" + Reg + "</i> "
            entry2 = entry
            entry = entry + subentry[i].findtext('L1')
            entry = entry.replace('{Italics}','<i>')
            entry = entry.replace('{/Italics}','</i>')
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            exampleList = []
            exampleList2 = []
            examples = subentry[i].findall('Ln')
            if examples:
                for j in range(0,len(examples)):
                    egID = examples[j].attrib.get('LnRef')
                    egElement = myapp.ui.dataIndex.exDict[egID]
                    eg = '<i>' + egElement.findtext('Line') + '</i>'
                    if len(egElement.findtext('L1Gloss')) != 0:
                        eg = eg + " ‘" + egElement.findtext('L1Gloss') + "’ (" #needs to allow for l2 option)
                    else:
                        eg = eg + " ‘" + egElement.findtext('L2Gloss') + "’ ("
                    eg = eg + egElement.attrib.get('Spkr') + ")"
                    eg = re.sub('{Italics}','',eg)
                    eg = re.sub('{/Italics}','',eg)
                    eg += "@" + egID
                    exampleList.append(eg)

                    eg2 = '<i>' + egElement.findtext('Line') + '</i>'
                    if len(egElement.findtext('L2Gloss')) != 0:
                        eg2 = eg2 + " ‘" + egElement.findtext('L2Gloss') + "’ (" #needs to allow for l2 option)
                    else:
                        eg2 = eg2 + " ‘" + egElement.findtext('L1Gloss') + "’ ("
                    eg2 = eg2 + egElement.attrib.get('Spkr') + ")"
                    eg2 = re.sub('{Italics}','',eg2)
                    eg2 = re.sub('{/Italics}','',eg2)
                    eg2 += "@" + egID
                    exampleList2.append(eg2)

            L1DefList.append([index,entry,exampleList])

            #L2
            try:
                entry2 = entry2 + subentry[i].findtext('L2')
                entry2 = entry2.replace('{Italics}','<i>')
                entry2 = entry2.replace('{/Italics}','</i>')
                entry2 = entry2.replace('{{','<')
                entry2 = entry2.replace('}}','>')
                L2DefList.append([index,entry2,exampleList2])
            except TypeError:
                pass
              
        if len(subentry) == 1:
            i = 0
            cWidth = 681
            myapp.ui.lL1Definition.setColumnCount(1)
            myapp.ui.lL2Definition.setColumnCount(1)
            myapp.ui.lL1Definition.setColumnWidth(0,cWidth)
            myapp.ui.lL2Definition.setColumnWidth(0,cWidth)
        else:
            i = 1
            cWidth = 645
            myapp.ui.lL1Definition.setColumnCount(2)
            myapp.ui.lL1Definition.setColumnWidth(0,25)
            myapp.ui.lL1Definition.setColumnWidth(1,cWidth)
            myapp.ui.lL2Definition.setColumnCount(2)
            myapp.ui.lL2Definition.setColumnWidth(0,25)
            myapp.ui.lL2Definition.setColumnWidth(1,cWidth)
        j = 0
        for item in L1DefList:
            myapp.ui.lL1Definition.insertRow(j)
            if i == 1:
                indexTag = item[0] + ")"
                tableCell = QtGui.QTableWidgetItem()
                tableCell.setText(indexTag)
                tableCell.setFlags(QtCore.Qt.ItemIsEnabled)
                myapp.ui.lL1Definition.setItem(j,0,tableCell)
            tableCell = QtGui.QTableWidgetItem()
            tableCell.setFlags(QtCore.Qt.ItemIsEnabled)
            tableCell.setTextAlignment(QtCore.Qt.TextWordWrap)
            text = cardLoader.breakLines(item[1], 100)
            tableCell.setText(text)
            tableCell.setSizeHint(QtCore.QSize(cWidth,16))
            myapp.ui.lL1Definition.setItem(j,i,tableCell)
            if len(item[2]) !=0:
                for eg in item[2]:
                    j += 1
                    myapp.ui.lL1Definition.insertRow(j)
                    tableCell = QtGui.QTableWidgetItem()
                    egIndex = eg.split("@")
                    text = cardLoader.breakLines(egIndex[0], 120,'&nbsp;&nbsp;&nbsp;')
                    tableCell.setText(text)
                    tableCell.setData(35,egIndex[1])
                    tableCell.setTextAlignment(QtCore.Qt.TextWordWrap)
                    tableCell.setFlags(QtCore.Qt.ItemIsEnabled)
                    myapp.ui.lL1Definition.setItem(j,i,tableCell)
                j += 1
        myapp.ui.lL1Definition.resizeRowsToContents()
        j = 0
        for item in L2DefList:
            myapp.ui.lL2Definition.insertRow(j)
            if i == 1:
                indexTag = item[0] + ")"
                tableCell = QtGui.QTableWidgetItem()
                tableCell.setText(indexTag)
                tableCell.setFlags(QtCore.Qt.ItemIsEnabled)
                myapp.ui.lL2Definition.setItem(j,0,tableCell)
            tableCell = QtGui.QTableWidgetItem()
            text = cardLoader.breakLines(item[1], 100)
            tableCell.setText(text)
            tableCell.setFlags(QtCore.Qt.ItemIsEnabled)
            tableCell.setTextAlignment(QtCore.Qt.TextWordWrap)
            myapp.ui.lL2Definition.setItem(j,i,tableCell)
            if len(item[2]) !=0:
                for eg in item[2]:
                    j += 1
                    myapp.ui.lL2Definition.insertRow(j)
                    tableCell = QtGui.QTableWidgetItem()
                    egIndex = eg.split("@")
                    text = cardLoader.breakLines(egIndex[0], 120,'&nbsp;&nbsp;&nbsp;')
                    tableCell.setText(text)
                    tableCell.setData(35,egIndex[1])
                    tableCell.setFlags(QtCore.Qt.ItemIsEnabled)
                    tableCell.setTextAlignment(QtCore.Qt.TextWordWrap)
                    myapp.ui.lL2Definition.setItem(j,i,tableCell)
            j += 1
        myapp.ui.lL2Definition.resizeRowsToContents()

    def loadLexCard(Fieldbook, lexRoot, navBtn=False):
          Fieldbook.ui.dataIndex.currentCard = lexRoot.attrib.get('LexID')
          Fieldbook.ui.dataIndex.lastLex = lexRoot.attrib.get('LexID')   
          Fieldbook.ui.dataIndex.root.set('LastLex',Fieldbook.ui.dataIndex.lastLex)
          if navBtn == False:
            Fieldbook.ui.tCardStack.addToQueue(Fieldbook,Fieldbook.ui.dataIndex.currentCard)
          
          try:
            _fromUtf8 = QtCore.QString.fromUtf8
          except AttributeError:
            _fromUtf8 = lambda s: s

          try:
              del(Fieldbook.ui.lGrammar.crossrefMenu)
          except AttributeError:
              pass
                
          try:
              del(Fieldbook.ui.lDialect.dialectMenu)
          except AttributeError:
              pass
          
          try:
              del(Fieldbook.ui.lL1Definition.L1DefinitionMenu)
          except AttributeError:
              pass
          
          try:
              del(Fieldbook.ui.lL2Definition.L2DefinitionMenu)
          except AttributeError:
              pass
          
          Fieldbook.ui.lOrthography.clear()
          entry = lexRoot.findtext('Orth')
          if entry:
            Fieldbook.ui.lOrthography.setText(entry)

          Fieldbook.ui.lPOS.clear()
          entry = lexRoot.findtext('POS')
          if entry:
            Fieldbook.ui.lPOS.setText(entry)

          Fieldbook.ui.lRegister.clear()
          entry = lexRoot.findtext('Reg')
          if entry:
            Fieldbook.ui.lRegister.setText(entry)

          Fieldbook.ui.lIPA.clear()
          entry = lexRoot.findtext('IPA')
          if entry:
            Fieldbook.ui.lIPA.setText(entry)

          Fieldbook.ui.lLiteral.clear()
          entry = lexRoot.findtext('Lit')
          if entry:
            entry = entry.replace('{ABB}','<small>')
            entry = entry.replace('{/ABB}','</small>')
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            Fieldbook.ui.lLiteral.setText(entry)

          #Grammar
          Fieldbook.ui.lGrammar.clear()
          subentry = lexRoot.findall('Grm')
          grmList = ''
          entryList = []
          refList = []
          if len(subentry) != 0:
            for i in range(0,len(subentry)):
                if subentry[i].attrib.get('Prefix'):
                    entry = "<i>" + subentry[i].attrib.get('Prefix') + ".</i> " + subentry[i].text
                else:
                    entry = subentry[i].text
                entry += "<br/>"
                entry = entry.replace('{{','<')
                entry = entry.replace('}}','>')
                grmList += entry
                if subentry[i].attrib.get('MediaRef'):
                  entryList.append(subentry[i].text)
                  refList.append(subentry[i].attrib.get('MediaRef'))
            Fieldbook.ui.lGrammar.insertHtml(grmList)
              
          subentry = lexRoot.findall('C2')
          if subentry:
            c2List = '<i>also</i> '
            for i in range(0,len(subentry)):
                entry = subentry[i].text
                if subentry[i].attrib.get('MediaRef'):
                  entryList.append(entry)
                  refList.append(subentry[i].attrib.get('MediaRef'))
                c2List = c2List + entry
                if i != len(subentry)-1:
                    c2List = c2List + ', '
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            if len(Fieldbook.ui.lGrammar.toPlainText()) != 0:
                c2List = "<br />" + c2List
            Fieldbook.ui.lGrammar.insertHtml(c2List)
            
          subentry = lexRoot.findall('Cf')
          if subentry:
            cfList = '<i>cf.</i> '
            for i in range(0,len(subentry)):
                entry = subentry[i].text
                if subentry[i].attrib.get('CrossRef'):
                   entryList.append(entry)
                   refList.append(subentry[i].attrib.get('CrossRef'))
                   cfList = cfList + entry
                else:
                    cfList = cfList + '<span style="color:blue">' + entry + '</span>'               
                if i != len(subentry)-1:
                    cfList = cfList + ', '
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            if len(Fieldbook.ui.lGrammar.toPlainText()) != 0:
                cfList = "<br />" + cfList
            Fieldbook.ui.lGrammar.insertHtml(cfList)
          if refList:
            field = 'lGrammar'
            cardLoader.buildContextMenu(field,refList,entryList)

          #Indices
          Fieldbook.ui.lPrimaryIndex.clear()
          entry = lexRoot.attrib.get('Index1')
          if entry:
            Fieldbook.ui.lPrimaryIndex.setPlainText(entry)

          Fieldbook.ui.lSecondaryIndex.clear()
          entry = lexRoot.attrib.get('Index2')
          if entry:
            Fieldbook.ui.lSecondaryIndex.setPlainText(entry)

          Fieldbook.ui.lNotes.clear()
          entry = lexRoot.findtext('Comments')
          if entry:
            entry = entry.replace('{{','<')
            entry = entry.replace('}}','>')
            Fieldbook.ui.lNotes.setText(entry)

          Fieldbook.ui.lKeywordIndex.clear()
          entry = lexRoot.attrib.get('Kywd')
          if entry:
            Fieldbook.ui.lKeywordIndex.setPlainText(entry)

          #Dialect
          Fieldbook.ui.lDialect.clear()
          dia = ''
          entry = ''
          subentry = lexRoot.find('Dia')
          if subentry != None:
              dialect = subentry.attrib.get('Dialect')
              entry = entry + " <i>" + dialect + "</i> "
              aNodeList = subentry.findall('Alternative')
              if len(aNodeList) != 0:
                  crossRefList = []
                  altList = []
                  j = 0
                  for item in aNodeList:
                      alternative = item.text
                      variant = item.attrib.get('Variant')
                      crossref = item.attrib.get('CrossRef')
                      if j == 0 and j == len(aNodeList) - 1:
                          entry = entry + " (" + variant + " " + alternative + ")"
                      elif j == 0:
                          entry = entry + " (" + variant + " " + alternative
                      elif j == len(aNodeList) - 1:
                          entry = entry + "; " + variant + " " + alternative + ")"
                      else:
                          entry = entry + "; " + variant + " " + alternative
                      j += 1
                      if crossref:
                          crossRefList.append(crossref)
                          altList.append(alternative)
                      if len(crossRefList) != 0:
                          field = 'lDialect'
                          cardLoader.buildContextMenu(field,crossRefList,altList)
              Fieldbook.ui.lDialect.insertHtml(entry)
                 
          Fieldbook.ui.lBrrw.clear()
          subentry = lexRoot.find('Brrw')
          if subentry != None:
              source = subentry.attrib.get('Source')
              cognate = lexRoot.findtext('Brrw')
              cognate = '“' + cognate + '”'
              borrowing = source + ' ' + cognate
              Fieldbook.ui.lBrrw.setPlainText(borrowing)

          #Metadata
          Fieldbook.ui.lSource.clear()
          Fieldbook.ui.lResearcher.clear()
          Fieldbook.ui.lDate.clear()
          Fieldbook.ui.lUpdated.clear()
          Fieldbook.ui.lConfirmed.clear()
          entry = lexRoot.attrib.get('Spkr')
          if entry:
            Fieldbook.ui.lSource.setPlainText(entry)
       
          entry = lexRoot.attrib.get('Rschr')
          if entry:
            Fieldbook.ui.lResearcher.setPlainText(entry)
            
          entry = lexRoot.attrib.get('Date')
          if entry:
            Fieldbook.ui.lDate.setPlainText(entry)

          entry = lexRoot.attrib.get('Update')
          if entry:
            Fieldbook.ui.lUpdated.setPlainText(entry)

          entry = lexRoot.attrib.get('Confirmed')
          if entry:
            Fieldbook.ui.lConfirmed.setPlainText(entry)

          #Definitions and examples
          cardLoader.loadDefinitions(lexRoot)
                      
          #Derivations
          Fieldbook.ui.lDerivatives.clear()
          Fieldbook.ui.lRemoveDerBtn.setEnabled(0)
          derivatives = lexRoot.findall('Drvn')
          parent = None
          if derivatives:
              Fieldbook.ui.lDerivatives.setAlternatingRowColors(True)
              for i in range(0,len(derivatives)):
                  derID = derivatives[i].attrib.get('LexIDREF')
                  der = Fieldbook.ui.dataIndex.lexDict[derID]
                  word = der.findtext('Orth')
                  POS = der.findtext('POS')
                  L1 = der.findtext('Def/L1')
                  text = word + " (" + POS + ") " + L1
                  item = QtGui.QListWidgetItem(parent, QtGui.QListWidgetItem.UserType)
                  item.setData(32, derID)
                  item.setText(text)
                  Fieldbook.ui.lDerivatives.addItem(item)
              Fieldbook.ui.lRemoveDerBtn.setEnabled(1)
              try:
                  Fieldbook.ui.lDerivatives.sortItems(QtCore.Qt.AscendingOrder)
              except AttributeError:
                  pass

          #Bases
          Fieldbook.ui.lBase.clear()
          Fieldbook.ui.lBreakLnkBtn.setEnabled(0)
          base = lexRoot.find('Root')
          if base != None:
              baseID = base.attrib.get('LexIDREF')
              baseElement = Fieldbook.ui.dataIndex.lexDict[baseID]
              baseName = baseElement.findtext('Orth')
              item = QtGui.QListWidgetItem(parent, QtGui.QListWidgetItem.UserType)
              item.setData(32, baseID)
              item.setText(baseName)
              Fieldbook.ui.lBase.addItem(item)
              Fieldbook.ui.lBreakLnkBtn.setEnabled(1)

          #Recordings
          Fieldbook.ui.lRecordings.clear()
          Fieldbook.ui.lSoundFileMeta.clear()
          media = lexRoot.findall('Sound')
          if media:
            for i in range(0,len(media)):
              mediaIndex = media[i].attrib.get('MediaRef')
              mediaElement = Fieldbook.ui.dataIndex.mediaDict[mediaIndex]
              recording = mediaElement.attrib.get('Filename')
              speaker = mediaElement.attrib.get('Spkr')
              date = mediaElement.attrib.get('Date')
              Fieldbook.ui.lRecordings.insertItem(i, recording)
              Fieldbook.ui.lRecordings.setItemData(i, mediaIndex,35)
            Fieldbook.ui.lRecordings.setCurrentIndex(0)
            label = Fieldbook.ui.lSoundFileMeta
            cardLoader.setMetaLabel(label,speaker,date)
            Fieldbook.ui.lRecordings.setEnabled(1)
            Fieldbook.ui.lDelEgBtn.setEnabled(1)          
          else:
            Fieldbook.ui.lRecordings.setEnabled(0)
            Fieldbook.ui.lDelEgBtn.setEnabled(0)          

    def setMetaLabel(label,speaker,date):
        label.setText(speaker + " " + date)

    ########## END OF LOAD CARD #############

    ########## LOAD CONTEXT MENUS ############

    def clearContextMenu(field):
          try:
              if field == 'lDialect':
                  del(myapp.ui.lDialect.dialectMenu)
              if field == 'lL1Definition':
                  del(myapp.ui.L1Definition.L1DefinitionMenu)
              if field == 'lL2Definition':
                  del(myapp.ui.L2Definition.L2DefinitionMenu)
              if field == 'lGrammar':
                  del(myapp.ui.lGrammar.crossrefMenu)
          except AttributeError:
              pass

    def updateContextMenu(field, linksList, altList):
          if field == 'lDialect':
              try:
                  myapp.ui.lDialect.dialectMenu.clear()
              except AttributeError:
                  myapp.ui.lDialect.dialectMenu = linksMenu()
              actionHeader = 'Find...'
              myapp.ui.lDialect.dialectMenu.addAction(actionHeader)
              for i in range(0,len(linksList)):
                  actionLink = 'action' + linksList[i]
                  alternate = "   " + altList[i]
                  setattr(myapp.ui, actionLink, QtGui.QAction(alternate, myapp.ui.lDialect.dialectMenu))
                  action = getattr(myapp.ui, actionLink)
                  myapp.ui.lDialect.dialectMenu.addAction(action)
                  action.setData(linksList[i])
                  action.triggered.connect(myapp.ui.lDialect.dialectMenu.linkSelected)
                  
          if field == 'lL1Definition':
              try:
                  myapp.ui.lL1Definition.L1DefinitionMenu.clear()
              except AttributeError:
                  myapp.ui.lL1Definition.L1DefinitionMenu = linksMenu()
              actionHeader = 'Find...'
              myapp.ui.lL1Definition.L1DefinitionMenu.addAction(actionHeader)
              for i in range(0,len(linksList)):
                  actionLink = 'action' + linksList[i]
                  alternate = "   " + altList[i]
                  setattr(myapp.ui, actionLink, QtGui.QAction(alternate, myapp.ui.lL1Definition.L1DefinitionMenu))
                  action = getattr(myapp.ui, actionLink)
                  myapp.ui.lL1Definition.L1DefinitionMenu.addAction(action)
                  action.setData(linksList[i])
                  action.triggered.connect(myapp.ui.lL1Definition.L1DefinitionMenu.linkSelected)
              
              try:
                  myapp.ui.lL2Definition.L2DefinitionMenu.clear()
              except AttributeError:
                  myapp.ui.lL2Definition.L2DefinitionMenu = linksMenu()
              actionHeader = 'Find...'
              myapp.ui.lL2Definition.L2DefinitionMenu.addAction(actionHeader)
              for i in range(0,len(linksList)):
                  actionLink = 'action' + linksList[i]
                  alternate = "   " + altList[i]
                  setattr(myapp.ui, actionLink, QtGui.QAction(alternate, myapp.ui.lL2Definition.L2DefinitionMenu))
                  action = getattr(myapp.ui, actionLink)
                  myapp.ui.lL2Definition.L2DefinitionMenu.addAction(action)
                  action.setData(linksList[i])
                  action.triggered.connect(myapp.ui.lL2Definition.L2DefinitionMenu.linkSelected)

          if field == 'lGrammar':
              try:
                  myapp.ui.lGrammar.crossrefMenu.clear()
              except AttributeError:
                  myapp.ui.lGrammar.crossrefMenu = linksMenu()
              soundsList = []
              soundName = []
              refList = []
              refName = []
              for i in range(0,len(linksList)):             
                  if 'M' in linksList[i]:
                      soundsList.append(linksList[i])
                      soundName.append(altList[i])
                  else:
                      refList.append(linksList[i])
                      refName.append(altList[i])
              if len(soundsList) != 0:
                  actionHeader = 'Play...'
                  myapp.ui.lGrammar.crossrefMenu.addAction(actionHeader)
                  for j in range(0,len(soundsList)):
                      if soundsList[j]:
                          actionLink = 'action' + soundsList[j]
                          alternative = "   " + soundName[j]
                          setattr(myapp.ui, actionLink, QtGui.QAction(alternative, myapp.ui.lGrammar.crossrefMenu))
                          action = getattr(myapp.ui, actionLink)
                          myapp.ui.lGrammar.crossrefMenu.addAction(action)
                          action.setData(soundsList[j])
                          action.triggered.connect(myapp.ui.lGrammar.crossrefMenu.linkSelected)
              if len(refList) != 0:
                  actionHeader = 'Find...'
                  myapp.ui.lGrammar.crossrefMenu.addAction(actionHeader)
                  for k in range(0,len(refList)):
                      if refList[k]:
                          actionLink = 'action' + refList[k]
                          alternative = "   " + refName[k]
                          setattr(myapp.ui, actionLink, QtGui.QAction(alternative, myapp.ui.lGrammar.crossrefMenu))
                          action = getattr(myapp.ui, actionLink)
                          myapp.ui.lGrammar.crossrefMenu.addAction(action)
                          action.setData(refList[k])
                          action.triggered.connect(myapp.ui.lGrammar.crossrefMenu.linkSelected)              
          
    def buildContextMenu(field, linksList, altList):
        if field == 'lDialect':
            try:
                del(myapp.ui.lDialect.dialectMenu)
            except AttributeError:
                pass
            myapp.ui.lDialect.dialectMenu = linksMenu()
        if field == 'lL1Definition'or field == 'L2Definition':
            try:
                del(myapp.ui.lL1Definition.L1DefinitionMenu)
            except AttributeError:
                pass
            myapp.ui.lL1Definition.L1DefinitionMenu = linksMenu()

            try:
                del(myapp.ui.lL2Definition.L2DefinitionMenu)
            except AttributeError:
                pass
            myapp.ui.lL2Definition.L2DefinitionMenu = linksMenu()

        if field == 'lGrammar':
            try:
                del(myapp.ui.lGrammar.crossrefMenu)
            except AttributeError:
                pass
            myapp.ui.lGrammar.crossrefMenu = linksMenu()

        cardLoader.updateContextMenu(field, linksList, altList)

    def openContextMenu(field, position):
        try:
            if field == 'lDialect':
                myapp.ui.lDialect.dialectMenu.exec(myapp.ui.lDialect.mapToGlobal(position))
            if field == 'lL1Definition':
                myapp.ui.lL1Definition.L1DefinitionMenu.exec(myapp.ui.lL1Definition.mapToGlobal(position))
            if field == 'lL2Definition':
                myapp.ui.lL2Definition.L2DefinitionMenu.exec(myapp.ui.lL2Definition.mapToGlobal(position))
            if field == 'lGrammar':
                myapp.ui.lGrammar.crossrefMenu.exec(myapp.ui.lGrammar.mapToGlobal(position))
        except AttributeError:
            pass

  ######END LOAD CONTEXT MENUS#######

class linksMenu(QtGui.QMenu):
    
    def __init__(self):
        super(linksMenu, self).__init__()             

    def linkSelected(self):
        dataIndex = myapp.ui.dataIndex
        sender = self.sender()
        link = sender.data()
        if 'M' in link:
            caller = 'menu'
            btnCmds.playSound(caller,link)
        else:
            lexRoot = dataIndex.lexDict[link]
            cardLoader.loadLexCard(myapp, lexRoot, False)        

class btnCmds:
    
    def successMessage():
        print('it worked')

    '''metadata orthography buttons'''

    def oClearTransform():
        '''clear transform field'''
        myapp.ui.oOrder.clear()
        myapp.ui.oList.clearSelection()
        myapp.ui.oDeleteBtn.setEnabled(0)
        myapp.ui.oUpdateBtn.setEnabled(0)
        myapp.ui.oClearTransformBtn.setEnabled(0)   

    def oDelete():
        '''delete orthography'''
        myapp.ui.oOrder.clear()
        badRow = myapp.ui.oList.currentRow()
        badNode = myapp.ui.oList.item(badRow,0).data(36)
        myapp.ui.dataIndex.root.find('Orthographies').remove(badNode)
        if myapp.ui.dataIndex.root.find('Orthographies/Map') == None:
            myapp.ui.dataIndex.root.remove(myapp.ui.dataIndex.root.find('Orthographies'))
            try:
                del myapp.ui.dataIndex.root.attrib['Orth']
            except KeyError:
                pass
        myapp.ui.oDeleteBtn.setEnabled(0)
        myapp.ui.oUpdateBtn.setEnabled(0)
        myapp.ui.oClearTransformBtn.setEnabled(0)   
        myapp.ui.oList.removeRow(badRow)
        myapp.ui.dataIndex.unsavedEdit = 1

    def oNew():
        '''define new orthography'''
        myapp.ui.oList.clearSelection()
        orthManager = QtGui.QInputDialog()
        newName = orthManager.getText(orthManager,'New orthography','Enter name for new orthography')
        kind = 'export'
        if newName[1] != False:
            if myapp.ui.dataIndex.root.find('Orthographies') == None:
                root = myapp.ui.dataIndex.root
                elemList = list(root)
                elemList.reverse()
                for i, item in enumerate(elemList):
                    if item.tag == 'Media':
                        break
                    elif item.tag == 'Abbreviations':
                        break
                i = len(elemList) - i
                newOrthNode = etree.Element('Orthographies')
                root.insert(i,newOrthNode)
                newPrimeBox = QtGui.QMessageBox()
                newPrimeBox.setIcon(QtGui.QMessageBox.Question)
                newPrimeBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                newPrimeBox.setDefaultButton(QtGui.QMessageBox.Yes)
                newPrimeBox.setText('Set primary orthography?')
                newPrimeBox.setInformativeText('Use these transformations automatically to '
                                               'generate IPA forms of lexical items?')
                choice = newPrimeBox.exec_()
                if choice == QtGui.QMessageBox.Yes:
                    kind = 'primary'
                    myapp.ui.dataIndex.root.set('Orth',newName[0])
                elif choice == QtGui.QMessageBox.Cancel:
                    return
            newItem = etree.SubElement(myapp.ui.dataIndex.root.find('Orthographies'),'Map')
            newItem.text = myapp.ui.oOrder.toPlainText()
            newItem.set('Name',newName[0])
            newItem.set('Type',kind)
            i = myapp.ui.oList.rowCount()
            newOrth = QtGui.QTableWidgetItem(1001)
            newType = QtGui.QTableWidgetItem(1001)
            newOrth.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            newType.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            newOrth.setText(newName[0])
            newOrth.setData(36,newItem)
            newType.setText(kind)
            myapp.ui.oList.setRowCount(i+1)
            myapp.ui.oList.setItem(i,0,newOrth)
            myapp.ui.oList.setItem(i,1,newType)
            myapp.ui.oList.setRowHeight(i,20)
            myapp.ui.oList.selectRow(i)
            myapp.ui.oDeleteBtn.setEnabled(1)
            myapp.ui.oUpdateBtn.setEnabled(1)
            myapp.ui.oClearTransformBtn.setEnabled(1)   
            myapp.ui.dataIndex.unsavedEdit = 1

    def oUpdate():
        '''update changes to orthography'''
        newTrans = myapp.ui.oOrder.toPlainText()
        tRow = myapp.ui.oList.currentRow()
        tNode = myapp.ui.oList.item(tRow,0).data(36)
        tNode.text = newTrans
        myapp.ui.dataIndex.unsavedEdit = 1        

    def oClearTest():
        '''clear test fields'''
        myapp.ui.oOutput.clear()
        myapp.ui.oInput.clear()

    def oRandomTest(n):
        '''select random forms to test'''
        cRow = myapp.ui.oList.currentRow()
        ortho = myapp.ui.oList.item(cRow,0).text()
        for i in range(0,n):
            lexList = myapp.ui.dataIndex.lexDict
            node = choice(list(lexList.keys()))
            string = myapp.ui.dataIndex.lexDict[node].findtext('Orth')
            if i == 0:
                inPut = string
            else:
                inPut += "\n" + string
            IPA = Orthographies.testTransform(string)
            if i == 0:
                output = IPA
            else:
                output += "\n" + IPA
        myapp.ui.oInput.setPlainText(inPut)           
        myapp.ui.oOutput.setPlainText(output)           

    def oTest():
        '''test transformations on a string'''
        string = myapp.ui.oInput.toPlainText()
        IPA = Orthographies.testTransform(string)
        myapp.ui.oOutput.setPlainText(IPA)

    def oRandom():
        n = myapp.ui.oNumberBox.value()
        btnCmds.oRandomTest(n)

    def oNumber():
        n = myapp.ui.oNumberBox.value()
        btnCmds.oRandomTest(n)

    '''metadata researcher buttons'''

    def mRDataCheck(rCode):
        '''ensures minimal content and prevents duplication of researchers and codes'''
        if len(rCode) == 0 or len(myapp.ui.mResearcher.toPlainText()) == 0:
                missingDataBox = QtGui.QMessageBox()
                missingDataBox.setIcon(QtGui.QMessageBox.Warning)
                missingDataBox.setStandardButtons(QtGui.QMessageBox.Ok)
                missingDataBox.setDefaultButton(QtGui.QMessageBox.Ok)
                missingDataBox.setText('Missing data.')
                missingDataBox.setInformativeText('You must have a name and a researcher code for every '
                                                  'researcher. Please provide the missing information.')
                missingDataBox.exec_()
                return 'abort'
        for i in range(0,myapp.ui.mRTable.rowCount()):
            if myapp.ui.mRTable.item(i,0).text() == rCode:
                duplicateCodeBox = QtGui.QMessageBox()
                duplicateCodeBox.setIcon(QtGui.QMessageBox.Warning)
                duplicateCodeBox.setStandardButtons(QtGui.QMessageBox.Ok)
                duplicateCodeBox.setDefaultButton(QtGui.QMessageBox.Ok)
                duplicateCodeBox.setText('Duplicate speaker code.')
                duplicateCodeBox.setInformativeText('This code is already in use. Please provide a '
                                                    'unique code for this researcher.')
                duplicateCodeBox.exec_()
                return 'abort'
        return 'okay'

    def mRUpdate():
        '''update researcher metadata'''
        try:
            node = myapp.ui.mRTable.item(myapp.ui.mRTable.currentRow(),0).data(36)
        except AttributeError:
            return
        node.find('Name').text = myapp.ui.mResearcher.toPlainText()
        try:
            node.find('Affiliation').text = myapp.ui.mAffiliation.toPlainText()
        except AttributeError:
            pass
        try:
            node.find('Info').text = myapp.ui.mRInfo.toPlainText()
        except AttributeError:
            pass
        try:
            level = myapp.ui.mPrivilegesBox.currentText()
        except AttributeError:
            level = 0
        if level == 'None':
            level = 0
        myapp.ui.mRTable.item(myapp.ui.mRTable.currentRow(),1).setText(myapp.ui.mResearcher.toPlainText())
        if level != 0:
            myapp.ui.mRTable.item(myapp.ui.mRTable.currentRow(),2).setText(level)
            node.set('Level',level)
            myapp.ui.mRTable.item(myapp.ui.mRTable.currentRow(),0).setData(40,level)
        else:
            myapp.ui.mRTable.item(myapp.ui.mRTable.currentRow(),2).setText(None)
            myapp.ui.mRTable.item(myapp.ui.mRTable.currentRow(),0).setData(40,None)
            try:
                del node.attrib['Level']
            except AttributeError:
                pass
        myapp.ui.mRTable.item(myapp.ui.mRTable.currentRow(),3).setText(myapp.ui.mAffiliation.toPlainText())
        myapp.ui.mRTable.item(myapp.ui.mRTable.currentRow(),4).setText(myapp.ui.mRInfo.toPlainText())
        for j in range(0,myapp.ui.mRTable.columnCount()-1):
            myapp.ui.mRTable.resizeColumnToContents(j)
            if myapp.ui.mRTable.columnWidth(j) > 165:
                myapp.ui.mRTable.setColumnWidth(j,165)
        myapp.ui.mRTable.resizeColumnToContents(myapp.ui.mRTable.columnCount()-1)
        myapp.ui.dataIndex.unsavedEdit = 1
            
    def mRClear():
        '''clear researcher metadata entry fields'''
        myapp.ui.mResearcher.clear()
        myapp.ui.mRCode.clear()
        myapp.ui.mAffiliation.clear()
        myapp.ui.mRInfo.clear()
        myapp.ui.mRAddBtn.setEnabled(1)
        myapp.ui.mRUpdateBtn.setEnabled(0)
        myapp.ui.mRDelBtn.setEnabled(0)
        myapp.ui.mRCode.setReadOnly(0)
        myapp.ui.mPrivilegesBox.setCurrentIndex(-1)
        myapp.ui.mRTable.selectRow(-1)

    def mRAdd():
        '''add new researcher metadata'''
        rCode = myapp.ui.mRCode.toPlainText()
        status = btnCmds.mRDataCheck(rCode)
        if status == 'abort':
            return
        newRschr = etree.Element('Rschr',{'RCode':rCode})
        newName = etree.SubElement(newRschr,'Name')
        newName.text = myapp.ui.mResearcher.toPlainText()
        if len(myapp.ui.mAffiliation.toPlainText()) != 0:
            newAff = etree.SubElement(newRschr,'Affiliation')
            newAff.text = myapp.ui.mAffiliation.toPlainText()
        if len(myapp.ui.mRInfo.toPlainText()) != 0:
            newInfo = etree.SubElement(newRschr,'Info')
            newInfo.text = myapp.ui.mInfo.toPlainText()
        ##need to set level attrib
        if myapp.ui.mPrivilegesBox.currentIndex() != -1:
            level = myapp.ui.mPrivilegesBox.currentText()
        else:
            level = None
        if level == 'None':
            level = None
        if level != None:
            newRschr.set('Level',level)
        k = myapp.ui.dataIndex.root.find('Rschr')
        d = myapp.ui.dataIndex.root.getchildren().index(k)
        myapp.ui.dataIndex.root.insert(d,newRschr)
        name = myapp.ui.mResearcher.toPlainText()
        try:
            affiliation = newRschr.find('Affiliation').text
        except AttributeError:
            affiliation = None
        try:
            info = newRschr.find('Info').text
        except AttributeError:
            info = None
        dataList = [rCode,name,level,affiliation,info]
        myapp.ui.mRTable.insertRow(-1)
        newRow = myapp.ui.mRTable.rowCount()-1
        for i in range (0,5):
            newItem = QtGui.QTableWidgetItem(1001)
            if dataList[i] != None:
                itemText = dataList[i]
                newItem.setText(itemText)
                newItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            myapp.ui.mRTable.setItem(newRow,i,newItem)
        myapp.ui.mRTable.item(newRow,0).setData(36,newRschr)
        myapp.ui.mRTable.item(newRow,0).setData(40,level)
        for j in range(0,myapp.ui.mRTable.columnCount()-1):
            myapp.ui.mRTable.resizeColumnToContents(j)
        myapp.ui.mRTable.sortItems(0,QtCore.Qt.AscendingOrder)
        myapp.ui.mRTable.scrollToItem(newItem, QtGui.QAbstractItemView.PositionAtCenter)
        for j in range(0,myapp.ui.mRTable.columnCount()-1):
            myapp.ui.mRTable.resizeColumnToContents(j)
            if myapp.ui.mRTable.columnWidth(j) > 165:
                myapp.ui.mRTable.setColumnWidth(j,165)
        myapp.ui.mRTable.resizeColumnToContents(myapp.ui.mRTable.columnCount()-1)
        myapp.ui.dataIndex.unsavedEdit = 1       

    def mRDel():
        '''delete speaker metadata'''
        deletedCodeBox = QtGui.QMessageBox()
        deletedCodeBox.setIcon(QtGui.QMessageBox.Critical)
        purgeBtn = deletedCodeBox.addButton("Purge",QtGui.QMessageBox.ActionRole)
        purgeBtn.setToolTip("remove all instances of this code from database")
        deletedCodeBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        deletedCodeBox.setDefaultButton(QtGui.QMessageBox.Ok)
        deletedCodeBox.setText('Delete researcher code?')
        deletedCodeBox.setInformativeText('This code may be in use in the database and '
                                          'removing it could cause validation errors. '
                                          'Proceed with deletion?')
        choice = deletedCodeBox.exec_()
        if deletedCodeBox.clickedButton() == purgeBtn:
            print('purge')
        if choice == QtGui.QMessageBox.Ok:
            badRow = myapp.ui.mRTable.currentRow() 
            badNode = myapp.ui.mRTable.item(badRow,0).data(36)
            myapp.ui.mRTable.removeRow(badRow)
            myapp.ui.dataIndex.root.remove(badNode)

    '''metadata speaker buttons'''
    
    def mSpDataCheck(sCode):
        '''ensures minimal content and prevent lack of duplication for consultants and codes'''
        if len(sCode) == 0 or len(myapp.ui.mSpeaker.toPlainText()) == 0:
                missingDataBox = QtGui.QMessageBox()
                missingDataBox.setIcon(QtGui.QMessageBox.Warning)
                missingDataBox.setStandardButtons(QtGui.QMessageBox.Ok)
                missingDataBox.setDefaultButton(QtGui.QMessageBox.Ok)
                missingDataBox.setText('Missing data.')
                missingDataBox.setInformativeText('You must have a name and a speaker code for every '
                                                  'consultant. Please provide the missing information.')
                missingDataBox.exec_()
                return 'abort'
        for i in range(0,myapp.ui.mSpTable.rowCount()):
            if myapp.ui.mSpTable.item(i,0).text() == sCode:
                duplicateCodeBox = QtGui.QMessageBox()
                duplicateCodeBox.setIcon(QtGui.QMessageBox.Warning)
                duplicateCodeBox.setStandardButtons(QtGui.QMessageBox.Ok)
                duplicateCodeBox.setDefaultButton(QtGui.QMessageBox.Ok)
                duplicateCodeBox.setText('Duplicate speaker code.')
                duplicateCodeBox.setInformativeText('This code is already in use. Please provide a '
                                                    'unique code for this consultant.')
                duplicateCodeBox.exec_()
                return 'abort'
        return 'okay'

    def mSpUpdate():
        '''update speaker metadata'''
        try:
            node = myapp.ui.mSpTable.item(myapp.ui.mSpTable.currentRow(),0).data(36)
        except AttributeError:
            return
        node.find('Name').text = myapp.ui.mSpeaker.toPlainText()
        node.find('Birthdate').text = myapp.ui.mBirthday.toPlainText()
        node.find('Place').text = myapp.ui.mBirthplace.toPlainText()
        node.find('Info').text = myapp.ui.mInfo.toPlainText()
        myapp.ui.mSpTable.item(myapp.ui.mSpTable.currentRow(),1).setText(myapp.ui.mSpeaker.toPlainText())
        myapp.ui.mSpTable.item(myapp.ui.mSpTable.currentRow(),2).setText(myapp.ui.mBirthday.toPlainText())
        myapp.ui.mSpTable.item(myapp.ui.mSpTable.currentRow(),3).setText(myapp.ui.mBirthplace.toPlainText())
        myapp.ui.mSpTable.item(myapp.ui.mSpTable.currentRow(),4).setText(myapp.ui.mInfo.toPlainText())
        myapp.ui.dataIndex.unsavedEdit = 1
            
    def mSpClear():
        myapp.ui.mSpeaker.clear()
        myapp.ui.mSCode.clear()
        myapp.ui.mBirthday.clear()
        myapp.ui.mBirthplace.clear()
        myapp.ui.mInfo.clear()
        myapp.ui.mSpAddBtn.setEnabled(1)
        myapp.ui.mSpDelBtn.setEnabled(0)
        myapp.ui.mSpUpdateBtn.setEnabled(0)
        myapp.ui.mSCode.setReadOnly(0)

    def mSpAdd():
        '''add new speaker metadata'''
        sCode = myapp.ui.mSCode.toPlainText()
        status = btnCmds.mSpDataCheck(sCode)
        if status == 'abort':
            return
        newSpkr = etree.Element('Speaker',{'SCode':sCode})
        newName = etree.SubElement(newSpkr,'Name')
        newName.text = myapp.ui.mSpeaker.toPlainText()
        if len(myapp.ui.mBirthday.toPlainText()) != 0:
            newBD = etree.SubElement(newSpkr,'Birthdate')
            newBD.text = myapp.ui.mBirthday.toPlainText()
        if len(myapp.ui.mBirthplace.toPlainText()) != 0:
            newBP = etree.SubElement(newSpkr,'Place')
            newBP.text = myapp.ui.mBirthplace.toPlainText()
        if len(myapp.ui.mInfo.toPlainText()) != 0:
            newInfo = etree.SubElement(newSpkr,'Info')
            newInfo.text = myapp.ui.mInfo.toPlainText()
        k = myapp.ui.dataIndex.root.find('Speaker')
        d = myapp.ui.dataIndex.root.getchildren().index(k)
        myapp.ui.dataIndex.root.insert(d,newSpkr)
        name = myapp.ui.mSpeaker.toPlainText()
        try:
            birthday = newSpkr.find('Birthdate').text
        except AttributeError:
            birthday = None
        try:
            place = newSpkr.find('Place').text
        except AttributeError:
            place = None
        try:
            info = newSpkr.find('Info').text
        except AttributeError:
            info = None
        dataList = [sCode,name,birthday,place,info]
        myapp.ui.mSpTable.insertRow(-1)
        newRow = myapp.ui.mSpTable.rowCount()-1
        for i in range (0,5):
            newItem = QtGui.QTableWidgetItem(1001)
            if dataList[i] != None:
                itemText = dataList[i]
                newItem.setText(itemText)
                newItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            myapp.ui.mSpTable.setItem(newRow,i,newItem)
        myapp.ui.mSpTable.item(newRow,0).setData(36,newSpkr)
        for j in range(0,myapp.ui.mSpTable.columnCount()-1):
            myapp.ui.mSpTable.resizeColumnToContents(j)
        myapp.ui.mSpTable.sortItems(0,QtCore.Qt.AscendingOrder)
        myapp.ui.mSpTable.scrollToItem(newItem, QtGui.QAbstractItemView.PositionAtCenter)
        myapp.ui.dataIndex.unsavedEdit = 1       

    def mSpDel():
        '''delete speaker metadata'''
        deletedCodeBox = QtGui.QMessageBox()
        deletedCodeBox.setIcon(QtGui.QMessageBox.Critical)
        purgeBtn = deletedCodeBox.addButton("Purge",QtGui.QMessageBox.ActionRole)
        purgeBtn.setToolTip("remove all instances of this code from database")
        deletedCodeBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        deletedCodeBox.setDefaultButton(QtGui.QMessageBox.Ok)
        deletedCodeBox.setText('Delete speaker code?')
        deletedCodeBox.setInformativeText('This code may be in use in the database and '
                                          'removing it could cause validation errors. '
                                          'Proceed with deletion?')
        choice = deletedCodeBox.exec_()
        if deletedCodeBox.clickedButton() == purgeBtn:
            print('purge')
        if choice == QtGui.QMessageBox.Ok:
            badRow = myapp.ui.mSpTable.currentRow() 
            badNode = myapp.ui.mSpTable.item(badRow,0).data(36)
            myapp.ui.mSpTable.removeRow(badRow)
            myapp.ui.dataIndex.root.remove(badNode)

    '''abbreviation data on example cards'''

    def addAbbr():
        '''add a new abbreviation to list'''
        aManager = abbrManager()
        if aManager.exec_():
            newData = aManager.setData()
            topNode = myapp.ui.dataIndex.root.find('Abbreviations')
            abbrList = []
            for child in topNode.iter('Abbr'):
                abbrList.append(child.attrib.get('ACode'))
            codeList = sorted(abbrList, key=lambda i : int(i[2:]))
            lastCode = codeList[-1]
            lastNumber = int(lastCode[2:])
            lastNumber += 1
            newCode = 'AC' + str(lastNumber)
            abbrev = etree.SubElement(topNode,'Abbr')
            abbrev.set('Abv',newData[0])
            abbrev.set('Term',newData[1])
            itemText = '<small>' + newData[0].swapcase() + '</small>&emsp;‘' + newData[1] + '’'
            if newData[2] != None:
                abbrev.set('Form',newData[2])
                itemText += ' (' + newData[2] + ')'
            ##generate ACode
            abbrev.set('ACode',newCode)
            print(etree.tostring(topNode,encoding='unicode'))
            newItem = QtGui.QTableWidgetItem(1001)
            newItem.setData(35,newCode)
            newItem.setData(36,abbrev)
            newItem.setText(itemText)
            newItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            nextRow = myapp.ui.eAbbreviations.rowCount()
            myapp.ui.eAbbreviations.setRowCount(nextRow+1)
            myapp.ui.eAbbreviations.setItem(nextRow,0,newItem)
            myapp.ui.eAbbreviations.setRowHeight(nextRow,20)
            myapp.ui.eAbbreviations.sortItems(0,QtCore.Qt.AscendingOrder)
            myapp.ui.eAbbreviations.scrollToItem(newItem, QtGui.QAbstractItemView.PositionAtCenter)
            myapp.ui.dataIndex.unsavedEdit = 1

    def delAbbr():
        '''remove abbreviation from list'''
        try:
            badNode = myapp.ui.eAbbreviations.currentItem().data(36)
            myapp.ui.eAbbreviations.removeRow(myapp.ui.eAbbreviations.currentRow())
        except AttributeError:
            return
        ##update XML
        myapp.ui.dataIndex.root.find('Abbreviations').remove(badNode)
        myapp.ui.dataIndex.unsavedEdit = 1

    def editAbbr():
        '''edit abbreviation in list'''
        try:
            abbrev = myapp.ui.eAbbreviations.currentItem().data(36)
        except AttributeError:
            return
        a = abbrev.attrib.get('Abv')
        b = abbrev.attrib.get('Term')
        try:
            c = abbrev.attrib.get('Form')
        except AttributeError:
            c = None
        oldData = [a,b,c]
        aManager = abbrManager()
        aManager.setAbbr(abbrev)
        if aManager.exec_():
            newData = aManager.setData()
            if oldData == newData:
                return
            else:
                abbrev.set('Abv',newData[0])
                abbrev.set('Term',newData[1])
                itemText = '<small>' + newData[0].swapcase() + '</small>&emsp;‘' + newData[1] + '’'
                if newData[2] != None:
                    abbrev.set('Form',newData[2])
                    itemText += ' (' + newData[2] + ')'
                else:
                    try:
                        del abbrev.attrib['Form']
                    except AttributeError:
                        pass
                myapp.ui.eAbbreviations.currentItem().setText(itemText)
                myapp.ui.dataIndex.unsavedEdit = 1       

    '''other buttons on example cards'''

    def toggleParse():
        if myapp.ui.eAutoParsingBtn.isChecked():
            myapp.ui.dataIndex.root.set('eParse','on')
        else:
            myapp.ui.dataIndex.root.set('eParse','off')
        myapp.ui.dataIndex.unsavedEdit = 1

    def eRemoveColumn():
        '''removes columns from analysis table'''
        myapp.ui.eAnalysis.removeColumn(myapp.ui.eAnalysis.currentColumn())
        mrphList = []
        ilegList = []
        mrph = None
        ileg = None
        for i in range(0,myapp.ui.eAnalysis.columnCount()):
            mrphList.append(myapp.ui.eAnalysis.item(0,i).text())
            ilegList.append(myapp.ui.eAnalysis.item(1,i).text())
        for item in mrphList:
            if mrph == None:
                mrph = item
            else:
                mrph += '\t' + item
        for item in ilegList:
            if ileg == None:
                ileg = item
            else:
                ileg += '\t' + item
        ileg = ileg.replace('<small>','{ABB}')
        ileg = ileg.replace('</small>','{/ABB}')
        ileg = ileg.replace('</small>','{{/ABB}}')
        ileg = ileg.replace('<small>','{{ABB}}')
        ileg = ileg.replace('<','{{')
        ileg = ileg.replace('>','}}')
        node = myapp.ui.dataIndex.exDict[myapp.ui.dataIndex.currentCard]
        node.find('Mrph').text = mrph
        node.find('ILEG').text = ileg
        myapp.ui.dataIndex.unsavedEdit = 1

    def eSplitEg():
        '''splits example between two cards'''
        oldID = myapp.ui.dataIndex.currentCard
        tSplitter = LineSplitter()
        tSplitter.fillForm(oldID)
        tSplitter.exec_()
        if tSplitter:
            idList = tSplitter.newData(oldID)
        else:
            return
        egRoot = myapp.ui.dataIndex.exDict[idList[1]]
        oldRoot = myapp.ui.dataIndex.exDict[idList[0]]
        try:
            source = myapp.ui.dataIndex.textDict[oldRoot.get('SourceText')]
        except KeyError:
            source = None
        ##update XML if this is from a text
        if source != None:
            lineList = source.findall('Ln')
            i = 2
            for line in lineList:
                if line.attrib.get('LnRef') == oldID:
                    newNode = etree.Element('Ln',{'LnRef':idList[1]})
                    source.insert(i,newNode)
                else:
                    i += 1
            ##update Text card if that text is open
            if oldRoot.get('SourceText') == myapp.ui.dataIndex.lastText and myapp.ui.tText.findChildren(textTable) != None:
                cardLoader.loadTextCard(myapp,source)                
        cardLoader.loadEgCard(myapp,egRoot)
        myapp.ui.dataIndex.unsavedEdit = 1
            
    def eLocateEg():
        '''goes to example in context (text or, eventually, dataset)'''
        egNode = myapp.ui.dataIndex.exDict[myapp.ui.dataIndex.currentCard]
        text = egNode.attrib.get('SourceText')
        if text == None:
            return
        if text == myapp.ui.dataIndex.lastText and myapp.ui.tText.findChildren(textTable) != None:
            myapp.ui.tabWidget.setCurrentIndex(2)
        else:
            cardLoader.loadTextCard(myapp,myapp.ui.dataIndex.textDict[text])
            myapp.ui.tabWidget.setCurrentIndex(2)                         

    def eAdd2Lex():
        '''adds example to a lexical entry'''
        eManager = EntryManager()
        eManager.listEntries()
        if eManager.exec_():
            data = eManager.setData()
            node = myapp.ui.dataIndex.lexDict[data[0]]
            definition = node.find('Def[@Index="%s"]' %str(data[1]))
            etree.SubElement(definition,'Ln',{'LnRef':myapp.ui.dataIndex.currentCard})
        myapp.ui.dataIndex.unsavedEdit = 1

    def eUpdateText():
        egNode = myapp.ui.dataIndex.exDict[myapp.ui.dataIndex.currentCard]
        text = egNode.attrib.get('SourceText')
        if text == None:
            return
        textNode = myapp.ui.dataIndex.textDict[text]
        if textNode != None:
            cardLoader.loadTextCard(myapp,textNode)
            myapp.ui.tabWidget.setCurrentIndex(2)
        myapp.ui.dataIndex.unsavedEdit = 1

    def eCopyLine():
        '''copies the current example to the clipboard'''
        node = myapp.ui.dataIndex.exDict[myapp.ui.dataIndex.currentCard]
        btnCmds.copyLine(node)

    '''buttons on text cards '''

    def tCopyLine():
        '''copies the selected line to the clipboard'''
        try:
            currentTable = myapp.ui.dataIndex.currentTextTable
            node = currentTable.item(0,0).data(35)
        except AttributeError:
            return
        btnCmds.copyLine(node)

    def tAnalyzeLine():
        '''take user to the example card for parsing/editing'''
        try:
            currentTable = int(myapp.ui.dataIndex.lineNumber) - 1
        except ValueError:
            return
        tableList = myapp.ui.tText.findChildren(textTable)
        egNode = tableList[currentTable].item(0,0).data(35)
        cardLoader.loadEgCard(myapp,egNode)
        myapp.ui.dataIndex.root.set('LastText',myapp.ui.dataIndex.currentCard)
        myapp.ui.tabWidget.setCurrentIndex(3)
        
    def tNewLine():
        update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
        ##step one: create a well-formed EG node and to add it to the XML
        date = myapp.ui.tDate.toPlainText()
        spkr = myapp.ui.tSource.toPlainText()
        rschr = myapp.ui.tResearcher.toPlainText()
        line = 'new line'
        gloss = 'new gloss'
        node = etree.Element('Ex')
        etree.SubElement(node,'Line')
        etree.SubElement(node,'L1Gloss')
        node.find('Line').text = line
        node.find('L1Gloss').text = gloss
        #step two: generate ID number (should try to do this with generateID method)
        codeList = sorted(myapp.ui.dataIndex.exDict.keys(), key=lambda i : int(i[2:]))
        topCode = int(codeList[-1][2:])
        topCode += 1
        ExID = 'EX' + str(topCode)
        while ExID in codeList:
            topCode += 1
            ExID = 'EX' + str(topCode)
        node.set('ExID',ExID)
        node.set('Date',date)
        node.set('Update',update)
        node.set('Spkr',spkr)
        node.set('Rschr',rschr)
        node.set('SourceText',myapp.ui.dataIndex.currentCard)
        k = myapp.ui.dataIndex.root.find('Ex')
        d = myapp.ui.dataIndex.root.getchildren().index(k)
        myapp.ui.dataIndex.root.insert(d,node)
        myapp.ui.dataIndex.exDict[ExID] = node
        ##step 3: build table
        newTable = cardLoader.textTableBuilder(node,ExID)
        ##step 4: rebuild tText
        try:
            currentTable = int(myapp.ui.dataIndex.lineNumber) - 1
        except ValueError:
            return
        tableList = myapp.ui.tText.findChildren(textTable)
        layoutList = myapp.ui.tText.findChildren(QtGui.QVBoxLayout)
        layout = layoutList[0]
        head = []
        for i in range(0,len(tableList)):
            if i == currentTable + 1:
                head.append(newTable)
            head.append(tableList[i])
        for table in tableList:
            table.setParent(None)
        j = 1    
        for table in head:
            table.item(0,0).setText(str(j))
            try:
                table.selectionData.openCell.setSelected(0)
            except RuntimeError:
                pass
            except AttributeError:
                pass
            table.selectionData.openCell = None
            layout.addWidget(table)
            j+=1
        myapp.ui.tText.adjustSize()
        ##step 6: update XML
        ExIDList = []
        for table in head:
            ExElem = table.item(0,0).data(35)
            ExIDList.append(ExElem.attrib.get('ExID'))
        for child in myapp.ui.dataIndex.root.iter('Text'):
            if child.attrib.get('TextID') == myapp.ui.dataIndex.currentCard:
                for node in child.findall('Ln'):
                    child.remove(node)
                i = 1
                for item in ExIDList:
                    newLn = etree.Element('Ln',{'LnRef':item})
                    child.insert(i,newLn)
                    i+=1
                child.set('Update', update)
                myapp.ui.tUpdated.setPlainText(update)
                break       
        myapp.ui.dataIndex.unsavedEdit = 1

    def tSplitLine():
        try:
            currentTable = int(myapp.ui.dataIndex.lineNumber) - 1
            myapp.ui.dataIndex.unsavedEdit = 1
        except ValueError:
            return
        tableList = myapp.ui.tText.findChildren(textTable)
        table = tableList[currentTable]
        oldID = table.item(0,0).data(35).attrib.get('ExID')
        tSplitter = LineSplitter()
        tSplitter.fillForm(oldID)
        tSplitter.exec_()
        if tSplitter:
            idList = tSplitter.newData(oldID)
        else:
            return
        ##step 4: rebuild tText
        for node in myapp.ui.dataIndex.root.iter('Ex'):
            if node.attrib.get('ExID') == idList[0]:
                newTable = cardLoader.textTableBuilder(node,idList[0])
                break
        for node in myapp.ui.dataIndex.root.iter('Ex'):
            if node.attrib.get('ExID') == idList[1]:
                newTable2 = cardLoader.textTableBuilder(node,idList[1])
                break
        table.setParent(None)
        tableList = myapp.ui.tText.findChildren(textTable)
        layoutList = myapp.ui.tText.findChildren(QtGui.QVBoxLayout)
        layout = layoutList[0]
        head = []
        for i in range(0,len(tableList)):
            if i == currentTable:
                head.append(newTable)
                head.append(newTable2)
            head.append(tableList[i])
        for table in tableList:
            table.setParent(None)
        j = 1
        for table in head:
            table.item(0,0).setText(str(j))
            table.selectionData.openCell = None
            layout.addWidget(table)
            j+=1
            
    def tRemoveLine():
        myapp.ui.dataIndex.unsavedEdit = 1
        update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
        ##step 1: rebuild tText
        try:
            currentTable = int(myapp.ui.dataIndex.lineNumber) - 1
        except ValueError:
            return
        myapp.ui.dataIndex.currentTextTable = None
        tableList = myapp.ui.tText.findChildren(textTable)
        layoutList = myapp.ui.tText.findChildren(QtGui.QVBoxLayout)
        layout = layoutList[0]
        head = []
        for i in range(0,len(tableList)):
            if i != currentTable:
                head.append(tableList[i])
            else:
                badEg = tableList[i].item(0,0).data(35)
                badID = badEg.attrib.get('ExID')
        for table in tableList:
            table.setParent(None)
        j = 1    
        for table in head:
            table.item(0,0).setText(str(j))
            table.selectionData.openCell = None
            table.selectionData.openCellText = ''
            table.selectionData.lineNumber = ''
            layout.addWidget(table)
            j+=1
        ##step 6: update XML
        ExIDList = []
        for table in head:
            ExElem = table.item(0,0).data(35)
            ExIDList.append(ExElem.attrib.get('ExID'))
        for child in myapp.ui.dataIndex.root.iter('Text'):
            if child.attrib.get('TextID') == myapp.ui.dataIndex.currentCard:
                for node in child.findall('Ln'):
                    child.remove(node)
                i = 1
                for item in ExIDList:
                    newLn = etree.Element('Ln',{'LnRef':item})
                    child.insert(i,newLn)
                    i+=1
                child.set('Update', update)
                myapp.ui.tUpdated.setPlainText(update)
                break
        expungeMessage = QtGui.QMessageBox()
        expungeMessage.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        expungeMessage.setDefaultButton(QtGui.QMessageBox.Yes)
        expungeMessage.setText('Expunge line from database?')
        expungeMessage.setInformativeText('This will remove the example and all cross-references permanently.')
        expungeMessage.exec_()
        if expungeMessage.result() == QtGui.QMessageBox.Yes:             
            for egNode in myapp.ui.dataIndex.root.iter('Ex'):
                if egNode.attrib.get('ExID') == badID:
                    myapp.ui.dataIndex.root.remove(egNode)
                    break
            target = 'Def/Ln[LnRef="' + badID + '"]'
            for lexNode in myapp.ui.dataIndex.root.iter('Lex'):
                if lexNode.find('Def/Ln[@LnRef="%s"]' % badID) != None:
                    lineNode = lexNode.find('Def/Ln[@LnRef="%s"]' % badID)
                    defList = lexNode.findall('Def')
                    for node in defList:
                        if node.find('Ln[@LnRef="%s"]' % badID) != None:
                            defNode = node
                            break
                    defNode.remove(lineNode)
            for dNode in myapp.ui.dataIndex.root.iter('Dset/Ln'):
                if dNode.attrib.get('LnRef') == badID:
                    myapp.ui.dataIndex.root.remove(dNode)
            ##will need to add index purge here, too
            
    '''buttons on lexicon card'''

    def addDrvn():
        dManager = DrvnManager()
        dManager.listEntries()
        exitFlag = 0
        if dManager.exec_():
            derivative = dManager.setData()
            current = myapp.ui.dataIndex.currentCard
            for child in myapp.ui.dataIndex.root.iter('Lex'):
                if child.attrib.get('LexID') == derivative:
                    if child.find('Root') != None:
                        if queryBox.result() == QtGui.QMessageBox.Ok:                            
                            try:                                   
                                child.remove(child.find('Root'))
                            except TypeError:
                                pass
                        else:
                            exitFlag = 1
                            break
                    elemList = child.getchildren()
                    i = 0
                    for item in elemList:
                        if item.tag != 'Def':
                            i += 1
                        else:
                            break                    
                    while child[i].tag == 'Def':
                        i += 1
                    while child[i].tag == 'Drvn':
                        i += 1
                    newBase = etree.Element('Root',{"LexIDREF":current})
                    child.insert(i,newBase)
                    item = QtGui.QListWidgetItem()
                    item.setData(32, derivative)
                    try:
                        text = child.findtext('Orth') + " (" + child.findtext('POS') + ") " + child.findtext('Def/L1')
                    except TypeError:
                        text = child.findtext('Orth') + " " + child.findtext('Def/L1')                        
                    item.setText(text)
                    myapp.ui.lDerivatives.addItem(item)
                    myapp.ui.lDerivatives.sortItems(QtCore.Qt.AscendingOrder)
                    myapp.ui.dataIndex.unsavedEdit = 1
                    break            
            for child in myapp.ui.dataIndex.root.iter('Lex'):
                if exitFlag == 1:
                    break
                if child.attrib.get('LexID') == current:
                    elemList = child.getchildren()
                    i = 0
                    for item in elemList:
                        if item.tag != 'Def':
                            i += 1
                        else:
                            break
                    while child[i].tag == 'Def':
                        i += 1
                    newDrvn = etree.Element('Drvn',{"LexIDREF":derivative})
                    child.insert(i,newDrvn)
                    print(etree.tostring(child,encoding='unicode'))
                    break
            myapp.ui.lRemoveDerBtn.setEnabled(1)

    def delDrvn():
        dManager = DrvnManager()
        dManager.listDerivatives()
        exitFlag = 0
        if dManager.exec_():
            derivative = dManager.setData()
            current = myapp.ui.dataIndex.currentCard
            for child in myapp.ui.dataIndex.root.iter('Lex'):
                if child.attrib.get('LexID') == derivative:
                    root = child.find('Root')
                    child.remove(root)
                    break
            for child in myapp.ui.dataIndex.root.iter('Lex'):
                if child.attrib.get('LexID') == current:
                    drvnList = child.findall('Drvn')
                    for item in drvnList:
                        if item.attrib.get('LexIDREF') == derivative:
                            badNode = item
                            break
                    child.remove(badNode)
                    for i in range(0,myapp.ui.lDerivatives.count()):
                        if myapp.ui.lDerivatives.item(i).data(32) == derivative:
                            badNode = myapp.ui.lDerivatives.takeItem(i)
                            del(badNode)
                            break
                    myapp.ui.dataIndex.unsavedEdit = 1
                    break
            if myapp.ui.lDerivatives.count() == 0:
                myapp.ui.lRemoveDerBtn.setEnabled(0)

    def addRoot():
        if myapp.ui.lBase.count() != 0:

            if queryBox.result() == QtGui.QMessageBox.Ok:
                btnCmds.makeDManager()
        else:
            btnCmds.makeDManager()
            myapp.ui.lBreakLnkBtn.setEnabled(1)

    def makeDManager():
        dManager = DrvnManager()
        dManager.listEntries()
        if dManager.exec_():
            base = dManager.setData()
            current = myapp.ui.dataIndex.currentCard
            for child in myapp.ui.dataIndex.root.iter('Lex'):
                if child.attrib.get('LexID') == base:
                    elemList = child.getchildren()
                    i = 0
                    for item in elemList:
                        if item.tag != 'Def':
                            i += 1
                        else:
                            break
                    while child[i].tag == 'Def':
                        i += 1
                    newDrvn = etree.Element('Drvn',{"LexIDREF":current})
                    child.insert(i,newDrvn)
                    text = child.findtext('Orth')
                    break
            for child in myapp.ui.dataIndex.root.iter('Lex'):
                if child.attrib.get('LexID') == current:
                    myapp.ui.lBase.clear()
                    try:
                        child.remove(child.find('Root'))
                    except TypeError:
                        pass
                    elemList = child.getchildren()
                    i = 0
                    for item in elemList:
                        if item.tag != 'Def':
                            i += 1
                        else:
                            break                    
                    while child[i].tag == 'Def':
                        i += 1
                    while child[i].tag == 'Drvn':
                        i += 1
                    newBase = etree.Element('Root',{"LexIDREF":base})
                    child.insert(i,newBase)
                    item = QtGui.QListWidgetItem()
                    item.setData(32, base)
                    item.setText(text)
                    myapp.ui.lBase.addItem(item)
                    myapp.ui.dataIndex.unsavedEdit = 1
                    break
                
    def removeRoot():
        '''this iter will remove the current card from the list of the root's derivations'''
        for child in myapp.ui.dataIndex.root.iter('Lex'):
            if child.attrib.get('LexID') == myapp.ui.lBase.item(0).data(32):
                for item in child.iter('Drvn'):
                    if item.get('LexIDREF') == myapp.ui.dataIndex.currentCard:
                        child.remove(item)
                        break
                break
        '''this iter will remove the root from the Lex entry of the current card'''
        for child in myapp.ui.dataIndex.root.iter('Lex'):
            if child.attrib.get('LexID') == myapp.ui.dataIndex.currentCard:
                root = child.find('Root')
                child.remove(root)
                break
        myapp.ui.lBase.clear()
        myapp.ui.lBreakLnkBtn.setEnabled(0)
        myapp.ui.dataIndex.unsavedEdit = 1

    def toggleAuto():
        if myapp.ui.lAutoBtn.isChecked():
            myapp.ui.dataIndex.root.set('lAuto','on')
            myapp.ui.lIPA.setEnabled(0)
        else:
            myapp.ui.dataIndex.root.set('lAuto','off')
            myapp.ui.lIPA.setEnabled(1)
        myapp.ui.dataIndex.unsavedEdit = 1

    '''copy examples to clipboard (all cards)'''

    def copyLine(node):
        L2Flag = 1
        entryRow0 = node.findtext('Line')
        exampleP = entryRow0
        exampleR = entryRow0
        try: 
            entryRow1 = node.findtext('Mrph')
            exampleP += "\r" + entryRow1
            exampleR += "<br />" + entryRow1
            entryRow2 = node.findtext('ILEG')
            exampleP += "\r" + entryRow2
            exampleR += "<br />" + entryRow2
        except AttributeError:
            pass
        try: 
            entryRow3 = node.findtext('L2Gloss')
        except AttributeError:
            L2Flag = 0
        if len(node.findtext('L1Gloss')) == 0:
            entryRow3 = node.findtext('L2Gloss')
            L2Flag = 0
        else:
            entryRow3 = node.findtext('L1Gloss')
        exampleP += "\r‘" + entryRow3 + "’"
        exampleR += "<br />&#8216;" + entryRow3 + "&#8217;"
        if L2Flag != 0:
            entryRow4 = node.findtext('L2Gloss')
            exampleP += "\r‘" + entryRow4 + "’"
            exampleR += "<br />&#8216;" + entryRow4 + "&#8217;"
        exampleP = exampleP.replace('{Italics}','')
        exampleP = exampleP.replace('{/Italics}','')
        exampleP = exampleP.replace('{{','')
        exampleP = exampleP.replace('}}','')
        exampleR = exampleR.replace('{Italics}','<i>')
        exampleR = exampleR.replace('{/Italics}','</i>')
        exampleR = exampleR.replace('{{','')
        exampleR = exampleR.replace('}}','')
        exampleR = exampleR.replace('–','&ndash;')
        clipboard = QtGui.QApplication.clipboard()
        clipping = QtCore.QMimeData()
        clipping.setText(exampleP)
        clipping.setHtml(exampleR)
        clipboard.setMimeData(clipping)

    '''media buttons (all cards)'''
    
    def lAddMedia():
        caller = myapp.ui.lRecordings
        mdField = myapp.ui.lSoundFileMeta
        btnCmds.newMedia(caller,mdField)

    def lDelMedia():
        if myapp.ui.lRecordings.count() != 0:
            caller = myapp.ui.lRecordings
            mdField = myapp.ui.lSoundFileMeta
            btnCmds.delMedia(caller,mdField)

    def tAddMedia():
        caller = myapp.ui.tRecordings
        mdField = myapp.ui.tSoundFileMeta
        btnCmds.newMedia(caller,mdField)

    def tDelMedia():
        if myapp.ui.tRecordings.count() != 0:
            caller = myapp.ui.tRecordings
            mdField = myapp.ui.tSoundFileMeta
            btnCmds.delMedia(caller,mdField)

    def eAddMedia():
        caller = myapp.ui.eRecordings
        mdField = myapp.ui.eSoundFileMeta
        btnCmds.newMedia(caller,mdField)

    def eDelMedia():
        if myapp.ui.eRecordings.count() != 0:
            caller = myapp.ui.eRecordings
            mdField = myapp.ui.eSoundFileMeta
            btnCmds.delMedia(caller,mdField)
   
    def dAddMedia():
        caller = myapp.ui.dRecordings
        mdField = myapp.ui.dSoundFileMeta
        btnCmds.newMedia(caller,mdField)

    def dDelMedia():
        if myapp.ui.dRecordings.count() != 0:
            caller = myapp.ui.dRecordings
            mdField = myapp.ui.dSoundFileMeta
            btnCmds.delMedia(caller,mdField)

    def mAddMedia():
        caller = myapp.ui.mMediaTable
        btnCmds.newMedia(caller)

    def mDelMedia():
        if myapp.ui.mMediaTable.currentRow() == -1:
            return
        msgbox = QtGui.QMessageBox()
        msgbox.setIcon(QtGui.QMessageBox.Warning)
        msgbox.setText("Remove recording.")
        msgbox.setInformativeText('This will remove all links to \n'
                                  'and information about this \n'
                                  'recording from the database. Proceed?')
        msgbox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
        msgbox.exec_()
        if msgbox.result() == QtGui.QMessageBox.Ok:
            myapp.ui.mMediaTable.removeRow(myapp.ui.mMediaTable.currentRow())
            myapp.ui.mMediaTable.setCurrentCell(-1,-1)
            print('purge')
            myapp.ui.dataIndex.unsavedEdit = 1

    def newMediaNode(newName):
        mManager = MediaManager()
        mManager.renameWindow(newName)
        if mManager.exec_():
            metaData = mManager.getValues()
            child = myapp.ui.dataIndex.root
            medID = idGenerator.generateID("MC",myapp.ui.dataIndex.mediaDict)
            elemList = list(child)
            elemList.reverse()
            for i, item in enumerate(elemList):
                if item.tag == 'Abbreviations':
                    break
            i = len(elemList) - i
            newNode = etree.Element('Media')
            child.insert(i,newNode)
            '''add attributes to media element'''
            newNode.set('MedID',medID)
            if len(metaData[0]) != 0:
                newNode.set('Spkr',metaData[0])
            if len(metaData[1]) != 0:
                newNode.set('Rschr',metaData[1])
            if len(metaData[2]) != 0:
                newNode.set('Date',metaData[2])
            if len(metaData[3]) != 0:
                newNode.set('Apparatus',metaData[3])
            if len(metaData[4]) != 0:
                newNode.set('Catalog',metaData[4])
            if len(metaData[5]) != 0:
                etree.SubElement(newNode,'Comments')
                newNode[0].text = metaData[5]
            if len(metaData[6]) != 0:
                newNode.set('FileType',metaData[6])
            if len(metaData[7]) != 0:
                newNode.set('Place',metaData[7])
            newNode.set('Filename',newName)
            myapp.ui.dataIndex.mediaDict[medID] = newNode
            metaData.append(medID)
            metaData.append(newNode)
            return metaData
        else:
            return False

    def newMedia(caller,mdField=None):
        newFile = QtGui.QFileDialog(myapp, "Add recordings.")
        newFile.setFileMode(QtGui.QFileDialog.ExistingFile)
        if newFile.exec_():
            newNames = newFile.selectedFiles()
            for item in newNames:
                sound2play = item
                newName = os.path.basename(item)
                if mdField != None:
                    if caller.findText(newName,QtCore.Qt.MatchExactly) == -1:
                        '''the recording is not linked to this card already'''
                        if myapp.ui.dataIndex.root.find('Media[@Filename="%s"]'%newName) != None:
                            '''the file is already linked into the database elsewhere'''
                            node = myapp.ui.dataIndex.root.find('Media[@Filename="%s"]'%newName)
                            if os.path.dirname(item) != myapp.ui.dataIndex.root.attrib.get('MediaFolder'):
                                file = node.attrib.get('Filename')
                                speaker = node.attrib.get('Spkr')
                                date = node.attrib.get('Date')
                                fileInfo = file + " [" + speaker + " " + date + "]"
                                msgbox = QtGui.QMessageBox()
                                msgbox.setText("File in database.")
                                msgbox.setInformativeText('There is already a recording named\n\n%s\n\nin the database. '
                                                          'If this is not the recording you are linking to, '
                                                          'select "Cancel" and rename the file.'%fileInfo)
                                msgbox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
                                msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
                                msgbox.exec_()
                                if msgbox.result() == QtGui.QMessageBox.Cancel:
                                    return                                
                            medID = node.get('MedID')
                        else:
                            '''completely new recording, create element and add metadata'''
                            metadata = btnCmds.newMediaNode(newName)
                            if metadata == False:
                                return
                            medID = metadata[8]
                            node = metadata[9]
                            if mdField != 'gManager':
                                mdField.setText(metadata[0] + ' ' + metadata[2])
                                child = myapp.ui.dataIndex.lexDict[myapp.ui.dataIndex.currentCard]
                                elemList = list(child)
                                elemList.reverse()
                                for i, item in enumerate(elemList):
                                    if item.tag == 'Comments':
                                        break
                                    elif item.tag == 'Root':
                                        break
                                    elif item.tag == 'Drvn':
                                        break
                                    elif item.tag =='Def':
                                        break
                                i = len(elemList) - i
                                newElem = etree.Element('Sound')
                                child.insert(i,newElem)
                                newElem.attrib['MediaRef'] = medID
                        thisItem = caller.insertItem(0,newName)
                        caller.setItemData(0,medID,35)
                        caller.setItemData(0,node,36)
                    else:
                        '''the recording is linked to this card already'''
                        msgbox = QtGui.QMessageBox()
                        msgbox.setText("Duplicate link.")
                        msgbox.setInformativeText('There is already a link to \n'
                                                  'a file with this name here.')
                        msgbox.setStandardButtons(QtGui.QMessageBox.Ok)
                        msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
                        msgbox.exec_()
                        return
                else:
                    '''add media elements to the media tab'''
                    if myapp.ui.dataIndex.root.find('Media[@Filename="%s"]'%newName) == None:
                        metadata = btnCmds.newMediaNode(newName)##
                        if metadata == False:
                            return
                        nextRow = caller.rowCount()
                        caller.setRowCount(nextRow+1)
                        firstItem = QtGui.QTableWidgetItem(1001)
                        firstItem.setText(newName)
                        firstItem.setData(36,metadata[9])
                        firstItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                        caller.setItem(nextRow,0,firstItem)
                        secondItem = QtGui.QTableWidgetItem(1001)
                        if len(metadata[0]) != 0:
                            secondItem.setText(metadata[0])
                            secondItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                            caller.setItem(nextRow,1,secondItem)
                        thirdItem = QtGui.QTableWidgetItem(1001)
                        if len(metadata[1]) != 0:
                            thirdItem.setText(metadata[1])
                            thirdItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                            caller.setItem(nextRow,2,thirdItem)
                        fourthItem = QtGui.QTableWidgetItem(1001)
                        fourthItem.setIcon(QtGui.QIcon(":/new/infoBtn.png"))
                        caller.setItem(nextRow,3,fourthItem)       
                        caller.sortItems(0,QtCore.Qt.AscendingOrder)
                        caller.scrollToItem(fourthItem, QtGui.QAbstractItemView.PositionAtCenter)
                        caller.selectRow(fourthItem.row())
                    else:
                        node = myapp.ui.dataIndex.root.find('Media[@Filename="%s"]'%newName)
                        if os.path.dirname(item) != myapp.ui.dataIndex.root.attrib.get('MediaFolder'):
                            file = node.attrib.get('Filename')
                            speaker = node.attrib.get('Spkr')
                            date = node.attrib.get('Date')
                            fileInfo = file + " [" + speaker + " " + date + "]"
                            msgbox = QtGui.QMessageBox()
                            msgbox.setText("Duplicate recording.")
                            msgbox.setInformativeText('There is already a recording named\n\n%s\n\nin the database. '
                                                      'If this is not the recording you are linking to, '
                                                      'rename the file and try again.'%fileInfo)
                            msgbox.setStandardButtons(QtGui.QMessageBox.Ok)
                            msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
                            msgbox.exec_()
                            return
            if mdField != None:
                caller.setCurrentIndex(caller.findText(newName,QtCore.Qt.MatchExactly))
                caller.setEnabled(1)
                if QtCore.QObject.objectName(mdField)[0] == 'l':
                    label = myapp.ui.lSoundFileMeta
                elif QtCore.QObject.objectName(mdField)[0] == 'e':
                    label = myapp.ui.eSoundfileMeta
                elif QtCore.QObject.objectName(mdField)[0] == 't':
                    label = myapp.ui.tSoundFileMeta
                elif QtCore.QObject.objectName(mdField)[0] == 'd':
                    label = myapp.ui.dSoundFileMeta
                speaker = node.get('Spkr')
                date = node.get('Date')
                cardLoader.setMetaLabel(label,speaker,date)
            QtGui.QSound.play(sound2play)
            myapp.ui.dataIndex.unsavedEdit = 1
            if mdField == 'gManager':
                return newNode

    def delMedia(caller,mdField):
        try:
            mdField.clear()
        except AttributeError:
            pass
        i = caller.currentIndex()
        medID = caller.itemData(i,35)
        msgbox = QtGui.QMessageBox()
        msgbox.setIcon(QtGui.QMessageBox.Warning)
        msgbox.setText("Remove recording.")
        msgbox.setInformativeText('This will remove the link to this \n'
                                  'media file. To remove this recording \n'
                                  'from the database, use the Media \n'
                                  'Manager on the Metadata tab.')
        msgbox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
        msgbox.exec_()
        if msgbox.result() == QtGui.QMessageBox.Ok:
            address = myapp.ui.dataIndex.currentCard
            if address[0] == "L":
                lexNode = myapp.ui.dataIndex.lexDict[address]
                if mdField != 'gManager':
                    if lexNode.find('Sound[@MediaRef="%s"]'%medID) != None:
                        badNode = lexNode.find('Sound[@MediaRef="%s"]'%medID)
                        lexNode.remove(badNode)
                else:
                    return lexNode
            elif address[0] == "E":
                egNode = myapp.ui.dataIndex.exDict[address]
                badNode = egNode.find('Sound[@MediaRef="%s"]'%medID)
                egNode.remove(badNode)
            elif address[0] == "D":
                dataNode = myapp.ui.dataIndex.dataDict[address]
                badNode = dataNode.find('Sound[@MediaRef="%s"]'%medID)
                dataNode.remove(badNode)
            elif address[0] == "T":
                textNode = myapp.ui.dataIndex.textDict[address]
                badNode = textNode.find('Sound[@MediaRef="%s"]'%medID)
                textNode.remove(badNode)
            caller.removeItem(i)
            ###need to enable/disable buttons
        myapp.ui.dataIndex.unsavedEdits = 1

    def lMediaInfo():
        if myapp.ui.lRecordings.count() != 0:
            caller = myapp.ui.lRecordings
            mdField = myapp.ui.lSoundFileMeta
            btnCmds.mediaInfo(caller,mdField)

    def tMediaInfo():
        if myapp.ui.tRecordings.count() != 0:
            caller = myapp.ui.tRecordings
            mdField = myapp.ui.tSoundFileMeta
            btnCmds.mediaInfo(caller,mdField)

    def eMediaInfo():
        if myapp.ui.eRecordings.count() != 0:
            caller = myapp.ui.eRecordings
            mdField = myapp.ui.eSoundFileMeta
            btnCmds.mediaInfo(caller,mdField)

    def dMediaInfo():
        if myapp.ui.dRecordings.count() != 0:
            caller = myapp.ui.dRecordings
            mdField = myapp.ui.dSoundFileMeta
            btnCmds.mediaInfo(caller,mdField)

    def mMediaInfo():
        caller = myapp.ui.mMediaTable
        btnCmds.mediaInfo(caller)

    def mediaInfo(caller,mdField=None):
        if mdField == None:
            i = caller.currentRow()
            mediaNode = caller.item(i,0).data(36)
            mediaID = mediaNode.attrib.get('MedID')
        else:
            i = caller.currentIndex()
            mediaID = caller.itemData(i,35)
        mManager = MediaManager()
        if mdField == None:
            mManager.renameWindow(mediaNode.attrib.get('Filename'))
        else:
            mManager.renameWindow(caller.currentText())
        mManager.setValues(mediaID)
        if myapp.ui.dataIndex.unsavedEdit == 1:
            toggleUE = 1
            myapp.ui.dataIndex.unsavedEdit = 0
        else:
            toggleUE = None
        if mManager.exec_() and myapp.ui.dataIndex.unsavedEdit == 1:
            metaData = mManager.getValues()
            for child in myapp.ui.dataIndex.root.iter('Media'):
                if child.attrib.get('MedID') == mediaID:
                    if len(metaData[0]) != 0:
                        child.set('Spkr',metaData[0])
                    if len(metaData[1]) != 0:
                        child.set('Rschr',metaData[1])
                    if len(metaData[2]) != 0:
                        child.set('Date',metaData[2])
                    if len(metaData[3]) != 0:
                        child.set('Apparatus',metaData[3])
                    if len(metaData[4]) != 0:
                        child.set('Catalog',metaData[4])
                    if len(metaData[5]) != 0:
                        if child.find('Comments') == None:
                            etree.SubElement(child,'Comments')
                            child[0].text = metaData[5]
                        else:
                            child.find('Comments').text = metaData[5]
                    if len(metaData[6]) != 0:
                        child.set('FileType',metaData[6])
                    if mdField != None:
                        mdField.setText(metaData[0] + " " + metaData[2])
                    else:
                        caller.item(i,1).setText(metaData[0])
                        caller.item(i,2).setText(metaData[1])
                    break
        if toggleUE != None:
            myapp.ui.dataIndex.unsavedEdit = 1               

    def lPlaySound():
        if myapp.ui.lRecordings.count() != 0:
            caller = myapp.ui.lRecordings
            btnCmds.playSound(caller)

    def tPlaySound():
        if myapp.ui.tRecordings.count() != 0:
            caller = myapp.ui.tRecordings
            btnCmds.playSound(caller)

    def ePlaySound():
        if myapp.ui.eRecordings.count() != 0:
            caller = myapp.ui.eRecordings
            btnCmds.playSound(caller)

    def dPlaySound():
        if myapp.ui.dRecordings.count() != 0:
            caller = myapp.ui.dRecordings
            btnCmds.playSound(caller)

    def mPlaySound():
        caller = myapp.ui.mMediaTable
        row = caller.currentRow()
        if row == -1:
            return
        node = caller.item(row,0).data(36)
        IDREF = node.attrib.get('MedID')
        btnCmds.playSound(caller, IDREF)       

    def playSound(caller, IDREF=None):
        if myapp.ui.dataIndex.root.get("MediaFolder"):
            prefix = myapp.ui.dataIndex.root.get("MediaFolder")
        else:
            prefix = None
        if IDREF != None:
            soundFile = myapp.ui.dataIndex.mediaDict[IDREF].get('Filename')
        else:
            soundFile = caller.currentText()
        if prefix != None:
            soundFile = prefix + "/" + soundFile
        if os.path.isfile(soundFile):
            QtGui.QSound.play(soundFile)            
        else:
            noFileBox = QtGui.QMessageBox()
            noFileBox.setIcon(QtGui.QMessageBox.Warning)
            noFileBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
            noFileBox.setDefaultButton(QtGui.QMessageBox.Ok)
            noFileBox.setText('Missing recording.')
            noFileBox.setInformativeText('Locate the missing file?')
            noFileBox.exec_()
            if noFileBox.result() == QtGui.QMessageBox.Ok:
                mFolder = QtGui.QFileDialog(myapp, "Find recording")
                mFolder.setFileMode(QtGui.QFileDialog.ExistingFile)
                mFolder.setOption(QtGui.QFileDialog.ReadOnly)
                if mFolder.exec_():
                    soundFile = mFolder.selectedFiles()[0]
                    setPathBox = QtGui.QMessageBox()
                    setPathBox.setIcon(QtGui.QMessageBox.Question)
                    setPathBox.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
                    setPathBox.setDefaultButton(QtGui.QMessageBox.Ok)
                    setPathBox.setText('Set default directory.')
                    setPathBox.setInformativeText('Use this directory as the default for locating recordings?')
                    setPathBox.exec_()
                    if setPathBox.result() == QtGui.QMessageBox.Ok:
                        prefix = os.path.dirname(soundFile)
                        myapp.ui.dataIndex.root.set("MediaFolder",prefix)
                        myapp.ui.dataIndex.unsavedEdit = 1
                    if os.path.isfile(soundFile):
                        QtGui.QSound.play(soundFile)     

    def mChooseDir():
        mFolder = QtGui.QFileDialog(myapp, "Choose a directory")
        mFolder.setFileMode(QtGui.QFileDialog.Directory)
        mFolder.setOption(QtGui.QFileDialog.ReadOnly)
        if mFolder.exec_():
            soundFile = mFolder.selectedFiles()[0]
            myapp.ui.dataIndex.root.set("MediaFolder",soundFile)
            myapp.ui.dataIndex.unsavedEdit = 1
            
    '''navigation buttons'''
    
    def btnForward():
        myapp.ui.tCardStack.goToCard(+1)

    def btnBack():
        myapp.ui.tCardStack.goToCard(-1)

    def lastLxCard():
        navBar = myapp.ui.lLexNav
        dct = myapp.ui.dataIndex.lexDict
        targetCard = btnCmds.lastCard(navBar,dct)
        cardLoader.loadLexCard(myapp, targetCard)

    def lastTxtCard():
        navBar = myapp.ui.tTextNav
        dct = myapp.ui.dataIndex.textDict
        targetCard = btnCmds.lastCard(navBar,dct)
        cardLoader.loadTextCard(myapp, targetCard)

    def lastEgCard():
        egList = list(myapp.ui.dataIndex.exDict.keys())
        targetCard = myapp.ui.dataIndex.exDict[egList[len(myapp.ui.dataIndex.exDict)-1]]
        cardLoader.loadEgCard(myapp, targetCard)

    def lastDsetCard():
        navBar = myapp.ui.dDataNav
        dct = myapp.ui.dataIndex.dataDict
        targetCard = btnCmds.lastCard(navBar,dct)
        cardLoader.loadDataCard(myapp, targetCard)

    def lastCard(navBar,dct):
        lastItem = navBar.model().rowCount() - 1
        data = navBar.model().index(lastItem,0).data(32)
        targetCard = dct[data]
        navBar.setCurrentIndex(navBar.model().index(lastItem,0))
        navBar.scrollTo(navBar.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)
        return targetCard
        
    def firstLxCard():
        navBar = myapp.ui.lLexNav
        dct = myapp.ui.dataIndex.lexDict
        targetCard = btnCmds.firstCard(navBar,dct)
        cardLoader.loadLexCard(myapp, targetCard)

    def firstTxtCard():
        navBar = myapp.ui.tTextNav
        dct = myapp.ui.dataIndex.textDict
        targetCard = btnCmds.firstCard(navBar,dct)
        cardLoader.loadTextCard(myapp, targetCard)

    def firstEgCard():
        egList = list(myapp.ui.dataIndex.exDict.keys())
        targetCard = myapp.ui.dataIndex.exDict[egList[0]]
        cardLoader.loadEgCard(myapp, targetCard)

    def firstDsetCard():
        navBar = myapp.ui.dDataNav
        dct = myapp.ui.dataIndex.dataDict
        targetCard = btnCmds.firstCard(navBar,dct)
        cardLoader.loadDataCard(myapp, targetCard)

    def firstCard(navBar,dct):
        data = navBar.model().index(0,0).data(32)
        targetCard = dct[data]
        navBar.setCurrentIndex(navBar.model().index(0,0))
        navBar.scrollTo(navBar.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)
        return targetCard

    def goPrevLx():
        navBar = myapp.ui.lLexNav
        dct = myapp.ui.dataIndex.lexDict
        targetCard = btnCmds.goPrev(navBar,dct)
        cardLoader.loadLexCard(myapp,targetCard)

    def goPrevEg():
        currentID = myapp.ui.dataIndex.currentCard               
        i = 1
        for child in myapp.ui.dataIndex.root.iter('Ex'):
            if child.attrib.get('ExID') != currentID:
                prevID = child.attrib.get('ExID')
                i += 1
            else:
                if i != 1:
                    targetID = prevID                       
        targetCard = myapp.ui.dataIndex.exDict[prevID]
        cardLoader.loadEgCard(myapp, targetCard)
        
    def goPrevTxt():
        navBar = myapp.ui.tTextNav
        dct = myapp.ui.dataIndex.textDict
        targetCard = btnCmds.goPrev(navBar,dct)
        cardLoader.loadTextCard(myapp,targetCard)

    def goPrevDset():
        navBar = myapp.ui.dDataNav
        dct = myapp.ui.dataIndex.dataDict
        targetCard = btnCmds.goPrev(navBar,dct)
        cardLoader.loadDataCard(myapp,targetCard)

    def goPrev(navBar,dct):
        try:
            if navBar.currentIndex().row() == 0:
                current = navBar.model().rowCount() - 1
            else:
                current = navBar.currentIndex().row() - 1
            navBar.setCurrentIndex(navBar.model().index(current,0))
            navBar.scrollTo(navBar.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)
            data = navBar.currentIndex().data(32)
            targetCard = dct[data]
            return targetCard
        except AttributeError:
            pass

    def goNextLx():
        navBar = myapp.ui.lLexNav
        dct = myapp.ui.dataIndex.lexDict
        targetCard = btnCmds.goNext(navBar,dct)
        cardLoader.loadLexCard(myapp,targetCard)

    def goNextEg():
        currentID = myapp.ui.dataIndex.currentCard
        getNextCard = 0
        for child in myapp.ui.dataIndex.root.iter('Ex'):
            if child.attrib.get('ExID') == currentID:
                getNextCard = 1
            else:
                if getNextCard == 1:
                    nextID = child.attrib.get('ExID')
                    break
        try:
            targetCard = myapp.ui.dataIndex.exDict[nextID]
        except UnboundLocalError:
            nextID = myapp.ui.dataIndex.root.find('Ex').attrib.get('ExID')
            targetCard = myapp.ui.dataIndex.exDict[nextID]
        cardLoader.loadEgCard(myapp, targetCard)
        
    def goNextTxt():
        navBar = myapp.ui.tTextNav
        dct = myapp.ui.dataIndex.textDict
        targetCard = btnCmds.goNext(navBar,dct)
        cardLoader.loadTextCard(myapp,targetCard)

    def goNextDset():
        navBar = myapp.ui.dDataNav
        dct = myapp.ui.dataIndex.dataDict
        targetCard = btnCmds.goNext(navBar,dct)
        cardLoader.loadDataCard(myapp,targetCard)

    def goNext(navBar,dct):
        if navBar.currentIndex().row() == navBar.model().rowCount() - 1:
            current = 0
        else:
            current = navBar.currentIndex().row() + 1
        navBar.setCurrentIndex(navBar.model().index(current,0))
        navBar.scrollTo(navBar.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)
        data = navBar.currentIndex().data(32)
        targetCard = dct[data]
        return targetCard
                
########## MAIN CLASS ############
########## MAIN CLASS ############
########## MAIN CLASS ############
      
class Fieldbook(QtGui.QMainWindow):
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.ui = Ui_Fieldbook()
    self.ui.setupUi(self)

    class Alphabetizer:

        def lNavSorter(navModelL):
            if self.ui.dataIndex.root.attrib.get('SortKey') == None:
                proxyModelL = QtGui.QSortFilterProxyModel()
                proxyModelL.setSourceModel(navModelL)
                proxyModelL.setSortCaseSensitivity(0)
                proxyModelL.sort(0,QtCore.Qt.AscendingOrder)
            return proxyModelL

        def resortProxyL(proxyModel):
            if self.ui.dataIndex.root.attrib.get('SortKey') == None:
                proxyModelL.setSortCaseSensitivity(0)
                proxyModelL.sort(0,QtCore.Qt.AscendingOrder)
                self.ui.lLexNav.scrollTo(self.ui.lLexNav.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)

    class focusOutFilter(QtCore.QObject):
        def __init__(self, parent):
            super(focusOutFilter, self).__init__(parent)
            self.lastContents = None

        def eventFilter(self, object, event):
            if event.type() == QtCore.QEvent.FocusIn:
                try:
                    object.clearSelection()
                except AttributeError:
                    pass
                if QtCore.QObject.objectName(object)[0] == 'e':
                    myapp.ui.eAnalysis.updateExample()
                    
            if event.type() == QtCore.QEvent.FocusOut:
                try:
                    object.clearSelection()
                except AttributeError:
                    pass
                try:
                    if myapp.ui.lDialect.dialectMenu.hasFocus():
                        return False
                except AttributeError:
                    pass
                if myapp.ui.dataIndex.unsavedEdit == 1:
                    fieldname = QtCore.QObject.objectName(object)
                    if QtCore.QObject.objectName(object) == "lDialect":
                        wordCount = myapp.ui.lDialect.toPlainText().split()
                        if len(wordCount) == 2:
                            self.dialectBox = QtGui.QMessageBox()
                            self.dialectBox.setIcon(QtGui.QMessageBox.Warning)
                            self.dialectBox.setStandardButtons(QtGui.QMessageBox.Cancel)
                            self.dialectBox.setStandardButtons(QtGui.QMessageBox.Ok)
                            self.dialectBox.setDefaultButton(QtGui.QMessageBox.Ok)
                            self.dialectBox.setText('Formatting error.')
                            self.dialectBox.setInformativeText('Format dialect information as'
                                                               '<blockquote><big>Cdn. (US. soda; UK fizzy drink)</big></blockquote>'
                                                               'For expressions known for only one dialect, simply<br /> '
                                                               'give the dialect name without an alternative.<br />')
                            self.dialectBox.exec_()
                            return False
                    if QtCore.QObject.objectName(object) == "lBrrw":
                        if len(myapp.ui.lBrrw.toPlainText().split(None,1)) == 1:
                            self.brrwBox = QtGui.QMessageBox()
                            self.brrwBox.setIcon(QtGui.QMessageBox.Warning)
                            self.brrwBox.setStandardButtons(QtGui.QMessageBox.Cancel)
                            self.brrwBox.setStandardButtons(QtGui.QMessageBox.Ok)
                            self.brrwBox.setDefaultButton(QtGui.QMessageBox.Ok)
                            self.brrwBox.setText('Formatting error.')
                            self.brrwBox.setInformativeText('The borrowings field must have both<br />'
                                                            'the abbreviated variant name and the <br />'
                                                            'alternative form, as in:'
                                                            '<blockquote><big>Sp. “nena”</big></blockquote>')
                            self.brrwBox.exec_()
                            return False
                    setContents(fieldname)
            return False
            

    ########### Start up scripts ########
    ########### define classes 
        
    '''settings'''
    
    settings = QtCore.QSettings()
    
    class dataIndexes:
      xmltree = None
      root = None
      lexDict = {}
      textDict = {}
      dataDict = {}
      exDict = {}
      mediaDict = {}
      speakerDict = {}
      rschrDict = {}
      unsavedEdit = 0
      recentFile = []
      sourceFile = None
      lastFile = None
      currentCard = None
      lastText = ''
      lastLex = ''
      lastEG = ''
      lastDset = ''
      lastDate = None
      lastSpeaker = None
      lastRschr = None
      lastApparatus = None
      lastPlace = None
      lastFileFormat = None
      lineNumber = ''
      currentTextTable = None
      
    self.ui.dataIndex = dataIndexes()


    class cardStack:
        '''class for moving forward and back'''
        theQueue = ['Home']
        theCounter = 0

        def goToCard(self,direction):
            #move through cards on buttonclicks, called by buttons
            if direction == -1:
                targetID = cardStack.theQueue[cardStack.theCounter-1]
                cardStack.theCounter = cardStack.theCounter - 1
                myapp.ui.lFwdBtn.setEnabled(1)
                myapp.ui.tFwdBtn.setEnabled(1)
                myapp.ui.eFwdBtn.setEnabled(1)
                myapp.ui.dFwdBtn.setEnabled(1)
            else:
                targetID = cardStack.theQueue[cardStack.theCounter+1]
                cardStack.theCounter += 1
                myapp.ui.lRtnBtn.setEnabled(1)
                myapp.ui.tRtnBtn.setEnabled(1)
                myapp.ui.eRtnBtn.setEnabled(1)
                myapp.ui.dRtnBtn.setEnabled(1)
            if len(cardStack.theQueue) - 1 == cardStack.theCounter:
                myapp.ui.lFwdBtn.setEnabled(0)
                myapp.ui.tFwdBtn.setEnabled(0)
                myapp.ui.eFwdBtn.setEnabled(0)
                myapp.ui.dFwdBtn.setEnabled(0)
            if cardStack.theCounter == 0:
                myapp.ui.lRtnBtn.setEnabled(0)
                myapp.ui.tRtnBtn.setEnabled(0)
                myapp.ui.eRtnBtn.setEnabled(0)
                myapp.ui.dRtnBtn.setEnabled(0)                
            if targetID[0] == "L":
                navBar = myapp.ui.lLexNav
                targetCard = myapp.ui.dataIndex.lexDict[targetID]
                cardLoader.loadLexCard(myapp, targetCard, navBtn=True)
                myapp.ui.tabWidget.setCurrentIndex(1)
            elif targetID[0] == "T":
                navBar = myapp.ui.tTextNav
                targetCard = myapp.ui.dataIndex.textDict[targetID]
                cardLoader.loadTextCard(myapp, targetCard, navBtn=True)
                myapp.ui.tabWidget.setCurrentIndex(2)
            elif targetID[0] == "E":
                targetCard = myapp.ui.dataIndex.exDict[targetID]
                if myapp.ui.dataIndex.unsavedEdit == 1:
                    pendingChange = 1
                else:
                    pendingChange = 0
                cardLoader.loadEgCard(myapp, targetCard, navBtn=True)
                myapp.ui.dataIndex.unsavedEdit = 0
                if pendingChange == 1:
                    myapp.ui.dataIndex.unsavedEdit = 1
                myapp.ui.tabWidget.setCurrentIndex(3)
            elif targetID[0] == "D":
                navBar = myapp.ui.dDataNav
                targetCard = myapp.ui.dataIndex.dataDict[targetID]
                cardLoader.loadDataCard(myapp, targetCard, navBtn=True)
                myapp.ui.tabWidget.setCurrentIndex(4)
            elif targetID[0] == "H":
                myapp.ui.tabWidget.setCurrentIndex(0)

            try:
                for i in range(0,navBar.model().rowCount()):
                    if navBar.model().index(i,0).data(32) == targetID:
                        theItem = i
                        break                    
                navBar.setCurrentIndex(navBar.model().index(theItem,0))
                navBar.scrollTo(navBar.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)
            except UnboundLocalError:
                myapp.ui.tabWidget.setCurrentIndex(0)                

        def addToQueue(self, fBook, currentCard):
            '''add card to list, remove from top if more than 20, called by cardloaders'''
            if cardStack.theQueue[cardStack.theCounter] != currentCard:
                if len(cardStack.theQueue) - 1 == cardStack.theCounter:
                    cardStack.theQueue.append(currentCard)
                else:
                    cardStack.theQueue = cardStack.theQueue[0:cardStack.theCounter+1]
                    cardStack.theQueue.append(currentCard)
                if len(cardStack.theQueue) <= 20:
                    cardStack.theCounter += 1
                else:
                    cardStack.theQueue.pop(0)
                    cardStack.theCounter = 19
                if cardStack.theCounter == 0:
                    fBook.ui.lRtnBtn.setEnabled(0)
                    fBook.ui.tRtnBtn.setEnabled(0)
                    fBook.ui.eRtnBtn.setEnabled(0)
                    fBook.ui.dRtnBtn.setEnabled(0)
                else:
                    fBook.ui.lRtnBtn.setEnabled(1)
                    fBook.ui.tRtnBtn.setEnabled(1)
                    fBook.ui.eRtnBtn.setEnabled(1)
                    fBook.ui.dRtnBtn.setEnabled(1)                    
                if cardStack.theCounter == len(cardStack.theQueue) - 1:
                    fBook.ui.lFwdBtn.setEnabled(0)
                    fBook.ui.tFwdBtn.setEnabled(0)
                    fBook.ui.eFwdBtn.setEnabled(0)
                    fBook.ui.dFwdBtn.setEnabled(0)
                else:
                    fBook.ui.lFwdBtn.setEnabled(1)
                    fBook.ui.tFwdBtn.setEnabled(1)
                    fBook.ui.eFwdBtn.setEnabled(1)
                    fBook.ui.dFwdBtn.setEnabled(1)
                   
    self.ui.tCardStack = cardStack()

    ####### define methods####
    
    def updateRecentFile(fileList, new = None):
        '''update for Open Recent file menu'''
        # configure recent files list
        self.ui.menuOpen_Recent.clear()
        if new == None:
            self.ui.actionRecent1 = QtGui.QAction(self)
            self.ui.actionRecent1.setObjectName('actionRecent1')
            self.ui.actionRecent2 = QtGui.QAction(self)
            self.ui.actionRecent2.setObjectName('actionRecent2')
            self.ui.actionRecent3 = QtGui.QAction(self)
            self.ui.actionRecent3.setObjectName('actionRecent3')
            self.ui.actionRecent4 = QtGui.QAction(self)
            self.ui.actionRecent4.setObjectName('actionRecent4')
            self.ui.actionRecent5 = QtGui.QAction(self)
            self.ui.actionRecent5.setObjectName('actionRecent5')
        else:
            if fileList == None:
              return
            newList = []
            newList.append(new)
            for i in range(0, len(fileList)):
              if newList.count(fileList[i]) == 0:
                newList.append(fileList[i])
            if len(newList) > 5:
              del newList[5:len(newList)-1]
            fileList = newList       
        if fileList == None:
            return
        shortNameList = []
        for i in range(0, len(fileList)):
            splitList = fileList[i].split("/")
            shortName = splitList[-1]
            if shortNameList.count(shortName) == 0:
              shortNameList.append(shortName)
            else:
              shortName = splitList[-2] + "/" + splitList[-1]
              shortNameList.append(shortName)
        # update recent files menu
        if len(shortNameList) >= 1:
            self.ui.menuOpen_Recent.addAction(self.ui.actionRecent1)
            self.ui.actionRecent1.setText(QtGui.QApplication.translate('Fieldbook', shortNameList[0], None, QtGui.QApplication.UnicodeUTF8))
        if len(shortNameList) >= 2:
            self.ui.menuOpen_Recent.addAction(self.ui.actionRecent2)
            self.ui.actionRecent2.setText(QtGui.QApplication.translate('Fieldbook', shortNameList[1], None, QtGui.QApplication.UnicodeUTF8))
        if len(shortNameList) >= 3:
            self.ui.menuOpen_Recent.addAction(self.ui.actionRecent3)
            self.ui.actionRecent3.setText(QtGui.QApplication.translate('Fieldbook', shortNameList[2], None, QtGui.QApplication.UnicodeUTF8))
        if len(shortNameList) >= 4:
            self.ui.menuOpen_Recent.addAction(self.ui.actionRecent4)
            self.ui.actionRecent4.setText(QtGui.QApplication.translate('Fieldbook', shortNameList[3], None, QtGui.QApplication.UnicodeUTF8))
        if len(shortNameList) >= 5:
            self.ui.menuOpen_Recent.addAction(self.ui.actionRecent5)
            self.ui.actionRecent5.setText(QtGui.QApplication.translate('Fieldbook', shortNameList[4], None, QtGui.QApplication.UnicodeUTF8))
        return fileList
    
    def setRecentFiles():
      if settings.value('RecentFile'):
        fname = settings.value('RecentFile')
        for i in range(0, len(fname)):
          if QtCore.QFile.exists(fname[i]):
             self.ui.dataIndex.recentFile.append(fname[i])
      updateRecentFile(self.ui.dataIndex.recentFile)

    setRecentFiles()        
    
    def flagUnsavedEdits():
        '''set flag when fields are edited'''
        self.ui.dataIndex.unsavedEdit = 1
        return self.ui.dataIndex.unsavedEdit
    

    def setSourceFile():
        '''determine the file to be opened on startup'''
        if settings.value('LastFile'):
            fname = settings.value('LastFile')
            if QtCore.QFile.exists(fname):
                self.ui.dataIndex.sourceFile = fname
                return self.ui.dataIndex.sourceFile
        else:
            fname = QtGui.QFileDialog.getOpenFileName(self, "Open...")
            if fname:
                self.ui.dataIndex.sourceFile = fname
            else:
                pass #this is a problem if user wants a new file and has no old file
        
    def giveWindowTitle():
      if self.ui.dataIndex.sourceFile != None:
        self.setWindowTitle("{0}[*]".format(os.path.basename(self.ui.dataIndex.sourceFile)))
      else:
       self.setWindowTitle("Electronic Fieldbook")        
        
    setSourceFile()
    giveWindowTitle()

    #####start up scripts ####
    
    '''Load and parse database file at startup'''
    try:
        self.ui.dataIndex.xmltree = etree.parse(self.ui.dataIndex.sourceFile)
    except TypeError:
        fname = QtGui.QFileDialog.getOpenFileName(self, "Open...")
        if fname:
            self.ui.dataIndex.sourceFile = fname
            self.ui.dataIndex.xmltree = etree.parse(self.ui.dataIndex.sourceFile)
        else:
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.tabWidget.setTabEnabled(1,0)
            self.ui.tabWidget.setTabEnabled(2,0)
            self.ui.tabWidget.setTabEnabled(3,0)
            self.ui.tabWidget.setTabEnabled(4,0)
            self.ui.tabWidget.setTabEnabled(5,0)
            self.ui.tabWidget.setTabEnabled(6,0)
            self.ui.tabWidget.setTabEnabled(7,0)
            self.ui.tabWidget.setTabEnabled(8,0)
            self.ui.dataIndex.lexDict.clear()
            self.ui.dataIndex.textDict.clear()
            self.ui.dataIndex.dataDict.clear()
            self.ui.hTitle.clear()
            self.ui.hLanguage.clear()
            self.ui.hFamily.clear()
            self.ui.hLocation.clear()
            self.ui.hPopulation.clear()
            self.ui.hISO.clear()
            self.ui.hLexNav.clear()
            self.ui.lLexNav.clear()
            self.ui.hTextNav.clear()
            self.ui.tTextNav.clear()      
            self.ui.hDataNav.clear()
            self.ui.dDataNav.clear()
            self.ui.hLexiconLabel.clear()
            self.ui.hTextsLabel.clear()
            self.ui.hDatasetLabel.clear()
            self.ui.dataIndex.recentFile = updateRecentFile(self.ui.dataIndex.recentFile, self.ui.dataIndex.sourceFile)
            self.ui.dataIndex.unsavedEdit = 0
            self.ui.dataIndex.sourceFile = None
            giveWindowTitle()
            return
    self.ui.dataIndex.root = self.ui.dataIndex.xmltree.getroot()
    self.ui.dataIndex.lastText = self.ui.dataIndex.root.attrib.get('LastText')
    self.ui.dataIndex.lastLex = self.ui.dataIndex.root.attrib.get('LastLex')
    self.ui.dataIndex.lastEG = self.ui.dataIndex.root.attrib.get('LastEG')
    self.ui.dataIndex.lastDset = self.ui.dataIndex.root.attrib.get('LastDset')

    '''Build and sort navigation list boxes for Home, Lexicon, Texts, and Dataset cards'''
    
    def sortNavLists(card,home):
        '''sorts the navigation boxes: card = the listwidget on the card,'''
        '''home = the listwidget on the home tab'''
        print('sorting')

    '''make models for the lex Navs'''
    navModelL = QtGui.QStandardItemModel()
    for node in self.ui.dataIndex.root.iter('Lex'):
        LexID = node.attrib.get('LexID')
        Orth = node.findtext('Orth')
        self.ui.dataIndex.lexDict[LexID] = node
        item = QtGui.QStandardItem(Orth)
        item.setData(LexID, 32)
        navModelL.appendRow(item)
##    proxyModelL = QtGui.QSortFilterProxyModel()
##    proxyModelL.setSourceModel(navModelL)
##    proxyModelL.setSortCaseSensitivity(0)
##    proxyModelL.sort(0,QtCore.Qt.AscendingOrder)
    proxyModelL = Alphabetizer.lNavSorter(navModelL)
    self.ui.hLexNav.setModel(proxyModelL)
    self.ui.lLexNav.setModel(proxyModelL)
    s = navModelL.rowCount()
    if s == 1:
        self.ui.hLexiconLabel.setText("Lexicon: 1 entry")
    else:
        self.ui.hLexiconLabel.setText("Lexicon: %d entries" % s)
    
##    Alphabetizer.navSorter(self.ui.lLexNav,self.ui.hLexNav)
    
    navModelT = QtGui.QStandardItemModel()
    for node in self.ui.dataIndex.root.iter('Text'):
        TextID = node.attrib.get('TextID')
        Title = node.findtext('Title')
        self.ui.dataIndex.textDict[TextID] = node
        item = QtGui.QStandardItem(Title)
        item.setData(TextID, 32)
        navModelT.appendRow(item)
    proxyModelT = QtGui.QSortFilterProxyModel()
    proxyModelT.setSourceModel(navModelT)
    proxyModelT.setSortCaseSensitivity(0)
    proxyModelT.sort(0,QtCore.Qt.AscendingOrder)
    self.ui.hTextNav.setModel(proxyModelT)
    self.ui.tTextNav.setModel(proxyModelT)
    s = navModelT.rowCount()
    if s == 1:
        self.ui.hTextsLabel.setText("Texts: 1 entry")
    else:
        self.ui.hTextsLabel.setText("Texts: %d entries" % s)

    navModelD = QtGui.QStandardItemModel()
    for node in self.ui.dataIndex.root.iter('Dset'):
        dsetID = node.attrib.get('DsetID')
        dTitle = node.findtext('Title')
        self.ui.dataIndex.dataDict[dsetID] = node
        item = QtGui.QStandardItem(dTitle)
        item.setData(dsetID, 32)
        navModelD.appendRow(item)
    proxyModelD = QtGui.QSortFilterProxyModel()
    proxyModelD.setSourceModel(navModelD)
    proxyModelD.setSortCaseSensitivity(0)
    proxyModelD.sort(0,QtCore.Qt.AscendingOrder)
    self.ui.hDataNav.setModel(proxyModelD)
    self.ui.dDataNav.setModel(proxyModelD)
    s = navModelD.rowCount()
    if s == 1:
        self.ui.hDatasetLabel.setText("Datasets: 1 dataset")
    else:
        self.ui.hDatasetLabel.setText("Datasets: %d datasets" % s)

    '''link the selection models of the navlists'''
    self.ui.hLexNav.setSelectionModel(self.ui.lLexNav.selectionModel())        
    self.ui.hTextNav.setSelectionModel(self.ui.tTextNav.selectionModel())        
    self.ui.hDataNav.setSelectionModel(self.ui.dDataNav.selectionModel())        

    '''build additional dictionaries to index examples and recordings'''

    for node in self.ui.dataIndex.root.iter('Ex'):
      ExID = node.attrib.get('ExID')
      self.ui.dataIndex.exDict[ExID] = node

    for node in self.ui.dataIndex.root.iter('Media'):
      MedID = node.attrib.get('MedID')
      self.ui.dataIndex.mediaDict[MedID] = node

    for node in self.ui.dataIndex.root.iter('Speaker'):
      spkrID = node.attrib.get('SCode')
      self.ui.dataIndex.speakerDict[spkrID] = node

    for node in self.ui.dataIndex.root.iter('Rschr'):
      rschr = node.attrib.get('RCode')
      self.ui.dataIndex.rschrDict[rschr] = node

    ############ end start up scripts ################

    '''tab navigation'''

    self.ui.tabWidget.setUsesScrollButtons(0)
    
    def leaveTab():
        if self.ui.tabWidget.currentIndex() == 0: #Home tab
            self.ui.actionNewCard.setEnabled(False)
            self.ui.actionDelCard.setEnabled(False)
            self.ui.actionIPA.setEnabled(False)
            self.ui.actionOrthographic.setEnabled(False) 
            self.ui.actionCustom.setEnabled(False) 
            self.ui.actionLoad_Schema.setEnabled(False)
            self.ui.actionAssistant.setEnabled(False)
            self.ui.menuOpen_Recent.setEnabled(True)
            self.ui.actionClose.setEnabled(True)
            self.ui.actionNew.setEnabled(True)
            self.ui.actionOpen.setEnabled(True)
            self.ui.tCardStack.addToQueue(self,'Home')
            self.ui.dataIndex.currentCard = 'Home'
        if self.ui.tabWidget.currentIndex() == 1: #Lexicon tab
            if self.ui.dataIndex.unsavedEdit == 1:
                pendingChange = 1
            else:
                pendingChange = 0
            lastLex = self.ui.dataIndex.root.attrib.get('LastLex')
            if lastLex:
                entry = self.ui.dataIndex.lexDict[lastLex]
                for i in range(0,self.ui.lLexNav.model().rowCount()):
                    if self.ui.lLexNav.model().index(i,0).data(32) == lastLex:
                        theItem = i
                        break                    
                self.ui.lLexNav.setCurrentIndex(self.ui.lLexNav.model().index(theItem,0))
                self.ui.lLexNav.scrollTo(self.ui.lLexNav.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)
                self.ui.dataIndex.currentCard = lastLex
            else:
                lastLex = self.ui.lLexNav.model().index(0,0).data(32)        
            self.ui.dataIndex.lastLex = lastLex
            entry = self.ui.dataIndex.lexDict[lastLex]
            cardLoader.loadLexCard(self, entry)
            self.ui.actionNewCard.setEnabled(True)
            self.ui.actionDelCard.setEnabled(True)
            self.ui.actionIPA.setEnabled(True)
            self.ui.actionOrthographic.setEnabled(True)
            self.ui.actionCustom.setEnabled(True) 
            self.ui.actionLoad_Schema.setEnabled(True)
            self.ui.actionAssistant.setEnabled(True)
            if pendingChange:
                self.ui.dataIndex.unsavedEdit = 1
            else:
                self.ui.dataIndex.unsavedEdit = 0
        if self.ui.tabWidget.currentIndex() == 2: #Texts tab
            if self.ui.dataIndex.unsavedEdit == 1:
                pendingChange = 1
            else:
                pendingChange = 0
            lastText = self.ui.dataIndex.root.attrib.get('LastText')
            self.ui.tNewLineBtn.setEnabled(0)
            self.ui.tSplitLineBtn.setEnabled(0)
            self.ui.tRemoveLineBtn.setEnabled(0)
            if lastText:
                entry = self.ui.dataIndex.textDict[lastText]
                for i in range(0,self.ui.tTextNav.model().rowCount()):
                    if self.ui.tTextNav.model().index(i,0).data(32) == lastText:
                        theItem = i
                        break                    
                self.ui.tTextNav.setCurrentIndex(self.ui.tTextNav.model().index(theItem,0))
                self.ui.tTextNav.scrollTo(self.ui.tTextNav.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)
                self.ui.dataIndex.currentCard = lastText
            entry = self.ui.dataIndex.textDict[lastText]
            cardLoader.loadTextCard(self, entry)
            myapp.ui.dataIndex.currentCard = lastText
            self.ui.actionNewCard.setEnabled(True)
            self.ui.actionDelCard.setEnabled(True)
            self.ui.actionIPA.setEnabled(True)
            self.ui.actionOrthographic.setEnabled(True)
            self.ui.actionCustom.setEnabled(True) 
            self.ui.actionLoad_Schema.setEnabled(True)
            self.ui.actionAssistant.setEnabled(True)
            if pendingChange:
                self.ui.dataIndex.unsavedEdit = 1
            else:
                self.ui.dataIndex.unsavedEdit = 0
        if self.ui.tabWidget.currentIndex() == 3: #Examples tab
            if self.ui.dataIndex.unsavedEdit == 1:
                pendingChange = 1
            else:
                pendingChange = 0
            lastEG = self.ui.dataIndex.root.attrib.get('LastEG')
            if lastEG:
              entry = self.ui.dataIndex.exDict[lastEG]
            else:
              entry = self.ui.dataIndex.root.find('Ex')
            cardLoader.loadEgCard(self, entry)
            self.ui.actionNewCard.setEnabled(True)
            self.ui.actionDelCard.setEnabled(True)
            self.ui.actionIPA.setEnabled(True)
            self.ui.actionOrthographic.setEnabled(True)
            self.ui.actionCustom.setEnabled(True) 
            self.ui.actionLoad_Schema.setEnabled(True)
            self.ui.actionAssistant.setEnabled(True)
            if pendingChange:
                self.ui.dataIndex.unsavedEdit = 1
            else:
                self.ui.dataIndex.unsavedEdit = 0
            self.ui.eAnalysis.selectionData.openCell = None
        if self.ui.tabWidget.currentIndex() == 4: #Datasets tab
            if self.ui.dataIndex.unsavedEdit == 1:
                pendingChange = 1
            else:
                pendingChange = 0
            lastDset = self.ui.dataIndex.root.attrib.get('LastDset')
            if lastDset:
                entry = self.ui.dataIndex.dataDict[lastDset]
                for i in range(0,self.ui.dDataNav.model().rowCount()):
                    if self.ui.dDataNav.model().index(i,0).data(32) == lastDset:
                        theItem = i
                        break                    
                self.ui.dDataNav.setCurrentIndex(self.ui.dDataNav.model().index(theItem,0))
                self.ui.dDataNav.scrollTo(self.ui.dDataNav.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)
                self.ui.dataIndex.currentCard = lastDset
            else:
                lastDset = self.ui.dataIndex.root.find('Dset')         
            entry = self.ui.dataIndex.dataDict[lastDset]
            cardLoader.loadDataCard(self, entry)
            self.ui.dataIndex.currentCard = lastDset
            self.ui.actionNewCard.setEnabled(True)
            self.ui.actionDelCard.setEnabled(True)
            self.ui.actionIPA.setEnabled(True)
            self.ui.actionOrthographic.setEnabled(True)
            self.ui.actionCustom.setEnabled(True) 
            self.ui.actionLoad_Schema.setEnabled(True)
            self.ui.actionAssistant.setEnabled(True)
            if pendingChange:
                self.ui.dataIndex.unsavedEdit = 1
            else:
                self.ui.dataIndex.unsavedEdit = 0
        if self.ui.tabWidget.currentIndex() == 5: #Concordances tab
            self.ui.actionNewCard.setEnabled(False)
            self.ui.actionDelCard.setEnabled(False)
            self.ui.actionIPA.setEnabled(False)
            self.ui.actionOrthographic.setEnabled(False) 
            self.ui.actionCustom.setEnabled(False) 
            self.ui.actionLoad_Schema.setEnabled(False)
            self.ui.actionAssistant.setEnabled(False)
            self.ui.dataIndex.currentCard = 'concordances'
        if self.ui.tabWidget.currentIndex() == 6: #Meta tab
            self.ui.actionNewCard.setEnabled(False)
            self.ui.actionDelCard.setEnabled(False)
            self.ui.actionIPA.setEnabled(False)
            self.ui.actionOrthographic.setEnabled(False) 
            self.ui.actionCustom.setEnabled(False) 
            self.ui.actionLoad_Schema.setEnabled(False)
            self.ui.actionAssistant.setEnabled(False)
            self.ui.dataIndex.currentCard = 'Meta'
        if self.ui.tabWidget.currentIndex() == 7: #Index tab
            self.ui.actionNewCard.setEnabled(False)
            self.ui.actionDelCard.setEnabled(False)
            self.ui.actionIPA.setEnabled(False)
            self.ui.actionOrthographic.setEnabled(False) 
            self.ui.actionCustom.setEnabled(False) 
            self.ui.actionLoad_Schema.setEnabled(False)
            self.ui.actionAssistant.setEnabled(False)
            self.ui.dataIndex.currentCard = 'index'

    self.ui.tabWidget.currentChanged.connect(leaveTab)

    ######### update XML ############

    def getCleanText(theText):
      if "<br />" in theText:
        theText = re.sub("<br />", "</p><p>", theText)
      if "</head>" in theText:
        a = theText.split('</head>')
        a.pop(0)
        theText = a[0]
        if "<p" in theText:
          b = theText.split("<p")
        else:
          b = theText.split("<li")
        theList = []
        for i in b:
          cut1 = i.find(">") + 1
          if "</p>" in i:
            cut2 = i.find("</p>")
          else:
            cut2 = i.find("</li>")
          i = i[cut1:cut2]
          theList.append(i)
      theList.pop(0)
      if "html" in theList[len(theList)-1]:
        theList.pop()
      return theList
      
    def formatHandler(theString):
      if "<" in theString:
        theString = theString.replace("<","{{")
        theString = theString.replace(">","}}")
      return theString

    def setContents(fieldname):
        '''update XML for updated fields'''
        
        if fieldname[0] == "l":
            update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
            self.ui.lUpdated.setPlainText(update)
            newContent = self.ui.lUpdated.toPlainText()
            child = self.ui.dataIndex.lexDict[self.ui.dataIndex.currentCard]
            child.set('Update',newContent)

        elif fieldname[0] == "t":
            update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
            self.ui.tUpdated.setPlainText(update)
            newContent = self.ui.tUpdated.toPlainText()
            child = self.ui.dataIndex.textDict[self.ui.dataIndex.currentCard]
            child.set('Update',newContent)

        elif fieldname[0] == "e":
            update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
            self.ui.eUpdated.setPlainText(update)
            newContent = self.ui.eUpdated.toPlainText()
            child = self.ui.dataIndex.exDict[self.ui.dataIndex.currentCard]
            child.set('Update',newContent)

        elif fieldname[0] == "d":
            update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
            self.ui.dUpdated.setPlainText(update)
            newContent = self.ui.dUpdated.toPlainText()
            child = self.ui.dataIndex.dataDict[self.ui.dataIndex.currentCard]
            child.set('Update',newContent)
      
        #Home tab
        if fieldname == 'hTitle':
            newContent = self.ui.hTitle.toPlainText()
            self.ui.dataIndex.root.set('Dbase',newContent)

        elif fieldname == 'hLanguage':
            newContent = self.ui.hLanguage.toPlainText()
            self.ui.dataIndex.root.set('Language',newContent)

        elif fieldname == 'hFamily':
            newContent = self.ui.hFamily.toPlainText()
            self.ui.dataIndex.root.set('Family',newContent)

        elif fieldname == 'hPopulation':
            newContent = self.ui.hPopulation.toPlainText()
            self.ui.dataIndex.root.set('Population',newContent)

        elif fieldname == 'hLocation':
            newContent = self.ui.hLocation.toPlainText()
            self.ui.dataIndex.root.set('Location',newContent)

        elif fieldname == 'hISO':
            newContent = self.ui.hISO.toPlainText()
            self.ui.dataIndex.root.set('ISO',newContent)           
            
        #Lexicon
        elif fieldname == 'lOrthography':
            newContent = self.ui.lOrthography.text()
            oldListText = child.find('Orth').text
            entryID = child.attrib.get('LexID')
            if newContent != oldListText:
                child.find('Orth').text = newContent
                currentProxyIndex = self.ui.lLexNav.currentIndex()
                currentSourceIndex = self.ui.lLexNav.model().mapToSource(currentProxyIndex)
                self.ui.lLexNav.model().sourceModel().itemFromIndex(currentSourceIndex).setText(newContent)
                Alphabetizer.resortProxyL(self.ui.lLexNav.model())
                
                '''if this was a homonym and now isn't in the same set, delink it'''
                if child.attrib.get('Hom') != None:
                    syn = child.attrib.get('Hom')
                    synList = syn.split(', ')
                    for card in synList:
                        del self.ui.dataIndex.lexDict[card].attrib['Hom']
                    synList.remove(entryID)
                    if len(synList) != 1:
                        for i, item in enumerate(synList):
                            if i == 0:
                                newSyn = item
                            else:
                                newSyn += ", " + item
                        for ID in synList:
                            self.ui.dataIndex.lexDict[ID].set('Hom', newSyn)

                '''check to see if you've created homonymy'''
                flag = False
                for node in self.ui.dataIndex.root.iter('Lex'):
                    if node.find('Orth').text == newContent and node.attrib.get('LexID') != entryID:
                        flag = True
                        break
                if flag == False:
                    return
                    
                '''if this is now homonymous with something else, link it in'''
                if node.attrib.get('Hom') != None:
                    '''revised word added to existing set'''
                    homAttr = node.attrib.get('Hom')
                else:
                    '''revised word creates new homonym set'''
                    homAttr = node.attrib.get('LexID')
                homAttr += ', ' + entryID
                homList = homAttr.split(', ')
                for card in homList:
                    self.ui.dataIndex.lexDict[card].set('Hom',homAttr)
                if self.ui.lAutoBtn.isChecked():
                    IPA = Orthographies.toIPA(newContent)
                    self.ui.lIPA.setText(IPA)
                    ipaNode = child.find('IPA')
                    if ipaNode != None:
                        child.remove(ipaNode)
                    if len(newContent) != 0:
                        elemList = list(child)
                        elemList.reverse()
                        for i,item in enumerate(elemList):
                            if item.tag == 'POS': 
                                break
                            elif item.tag == 'Orth': 
                                break
                        i = len(elemList) - i
                        child.insert(i,etree.Element('IPA'))
                        child.find('IPA').text = IPA

        elif fieldname == 'lPOS':
            newContent = self.ui.lPOS.toPlainText()
            posNode = child.find('POS')
            if posNode != None:
                child.remove(posNode)
            if len(newContent) != 0:
                child.insert(1,etree.Element('POS'))
                child.find('POS').text = newContent

        elif fieldname == 'lIPA':
            newContent = self.ui.lIPA.text()
            ipaNode = child.find('IPA')
            if ipaNode != None:
                child.remove(ipaNode)
            if len(newContent) != 0:
                elemList = list(child)
                elemList.reverse()
                for i,item in enumerate(elemList):
                    if item.tag == 'POS': 
                        break
                    elif item.tag == 'Orth': 
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('IPA'))
                child.find('IPA').text = newContent

        elif fieldname == 'lLiteral':
            cursor = QtGui.QTextCursor(self.ui.lLiteral.document())
            cursor.select(QtGui.QTextCursor.LineUnderCursor)
            newContent = cursor.selection().toHtml()
            refresh = cursor.selection().toPlainText() #add small caps formatting to abbreviations???
            if len(newContent) != 0:
                theList = newContent.split("<!--StartFragment-->")
                theList.pop(0)
                theList = theList[0].split("<!--EndFragment-->")
                theList.pop(1)
                newContent = formatHandler(theList[0])
            else:
                newContent = ''
            litNode = child.find('Lit')
            if litNode != None:
                child.remove(litNode)
            if len(newContent) != 0:
                elemList = list(child)
                for i, item in enumerate(elemList):
                    if item.tag == 'Def':
                        break
                child.insert(i,etree.Element('Lit'))
                child.find('Lit').text = newContent
                   
        elif fieldname == 'lRegister':
            newContent = self.ui.lRegister.toPlainText()
            regNode = child.find('Reg')
            if regNode != None:
                child.remove(regNode)
            if len(newContent) != 0:
                elemList = list(child)
                elemList.reverse()
                for i,item in enumerate(elemList):
                    if item.tag == 'Cf.':
                        break
                    elif item.tag == 'C2':
                        break
                    elif item.tag == 'Grm': 
                        break
                    elif item.tag == 'IPA': 
                        break
                    elif item.tag == 'POS': 
                        break
                    elif item.tag == 'Orth': 
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('Reg'))
                child.find('Reg').text = newContent
               
        elif fieldname == 'lDialect':
            newContent = self.ui.lDialect.toPlainText()
            alternate = ''
            if newContent:
                dialectList = newContent.split(None,1)
                dialect = dialectList[0]
                diaText = dialect
                altList = None
                if len(dialectList) > 1:
                    alternate = dialectList[1]              
                    alternate = re.sub("\(", "", alternate)
                    alternate = re.sub("\)", "", alternate)
                    altList = alternate.split("; ")
                    for i in range(0,len(altList)):
                        alternative = altList[i].split(None,1)
                        variant = alternative[0]
                        try:
                            alternate = alternative[1]
                        except IndexError:
                            self.dialectBox = QtGui.QMessageBox()
                            self.dialectBox.setIcon(QtGui.QMessageBox.Warning)
                            self.dialectBox.setStandardButtons(QtGui.QMessageBox.Cancel)
                            self.dialectBox.setStandardButtons(QtGui.QMessageBox.Ok)
                            self.dialectBox.setDefaultButton(QtGui.QMessageBox.Ok)
                            self.dialectBox.setText('Formatting error.')
                            self.dialectBox.setInformativeText('Format dialect information as'
                                                               '<blockquote><big>Cdn. (US. soda; UK fizzy drink)</big></blockquote>'
                                                               'For expressions known for only one dialect, simply<br /> '
                                                               'give the dialect name without an alternative.<br />')
                            self.dialectBox.exec_()
                            return
                        if i == 0 and len(altList) - 1 == 0:
                            dialect = dialect + " (" + variant + " " + alternate + ")"
                        elif i == 0:
                            dialect = dialect + " (" + variant + " " + alternate
                        elif i == len(altList) - 1:
                            dialect = dialect + "; " + variant + " " + alternate + ")"
                        else:
                            dialect = dialect + "; " + variant + " " + alternate
                    self.ui.lDialect.setPlainText(dialect)                    
            crossRef = None
            oldCrossRef = None
            if child.find('Dia') != None:
                oldAlt = child.findall('Dia/Alternative')
                oldCrossRef = []
                if oldAlt != None:
                    for item in oldAlt:
                        oldRef = item.attrib.get('CrossRef')
                        oldCrossRef.append(oldRef)
                child.remove(child.find('Dia'))
            if newContent:
                elemList = list(child)
                elemList.reverse()
                for i, item in enumerate(elemList):
                    if item.tag == 'Reg':
                        break
                    elif item.tag == 'Cf':
                        break
                    elif item.tag == 'C2':
                        break
                    elif item.tag == 'Grm':
                        break
                    elif item.tag == 'IPA':
                        break
                    elif item.tag == 'POS': 
                        break
                    elif item.tag == 'Orth': 
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('Dia',{'Dialect':diaText}))
                if altList != None and len(altList) != 0:
                    crossRefList = []
                    alterList = []
                    for j in range(0,len(altList)):
                        altParts = altList[j].split(None,1)
                        variant = altParts[0]
                        alternate = altParts[1]
                        newAltNode = etree.SubElement(child.find('Dia'),'Alternative',{'Variant':variant})
                        newAltNode.text = alternate
                        for entry in self.ui.dataIndex.root.iter('Lex'):
                            lexeme = entry.find('Orth').text
                            if lexeme == alternate and entry.attrib.get('Hom') != None:
                                for oldRef in oldCrossRef:
                                    if entry.attrib.get('LexID') == oldRef:
                                        crossRef = oldRef
                                        newAltNode.set('CrossRef',crossRef)
                                        break
                                    else: 
                                        synList = entry.attrib.get('Hom').split(", ")
                                        for syn in synList:
                                            if entry.attrib.get('LexID') == oldCrossRef:
                                               crossRef = oldRef
                                               newAltNode.set('CrossRef',crossRef)
                                               break
                                        synList.append(entry.attrib.get('LexID'))
                                        newCf = crossRefManager()
                                        newCf.setRefs(synList)
                                        if newCf.exec_():
                                            crossRef = newCf.getRef()
                                        else:
                                            crossRef = None
                                        break
                                
                            elif lexeme == alternate:
                                crossRef = entry.attrib.get('LexID')
                                newAltNode.set('CrossRef',crossRef)
                                break
                        if crossRef != None:
                            crossRefList.append(crossRef)
                            alterList.append(alternate)
                    if crossRefList != None:
                        cardLoader.updateContextMenu(fieldname,crossRefList,alterList)
                    if crossRefList == None:
                        cardLoader.clearContextMenu(fieldname)
           
        elif fieldname == 'lBrrw':
            newContent = self.ui.lBrrw.toPlainText()
            if newContent:
                borrowing = newContent.split(None,1)
                source = borrowing[0]
                cognate = borrowing[1]
                cognate = re.sub('"', '', cognate)
                cognate = re.sub('“', '', cognate)
                cognate = re.sub('”', '', cognate)
                newText = source + ' “' + cognate + '”'
                self.ui.lBrrw.setPlainText(newText)
            borrowNode = child.find('Brrw')
            if borrowNode != None:
                child.remove(borrowNode)
            if newContent:
                elemList = list(child)
                elemList.reverse()
                for i, item in enumerate(elemList):
                    if item.tag == 'Dia':
                        break
                    elif item.tag == 'Reg':
                        break
                    elif item.tag == 'Cf.':
                        break
                    elif item.tag == 'C2':
                        break
                    elif item.tag == 'Grm': 
                        break
                    elif item.tag == 'IPA': 
                        break
                    elif item.tag == 'POS': 
                        break
                    elif item.tag == 'Orth': 
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('Brrw'))
                child.find('Brrw').text = cognate
                child.find('Brrw').set('Source',source)
                
        elif fieldname == 'lGrammar':
            newText = self.ui.lGrammar.toPlainText()
            fullList = newText.split('\n')
            if len(fullList[-1]) == 0:
                del fullList[-1]
            newText = re.sub('\n','<br />',newText)
            newText = re.sub('cf.','<i>cf.</i>',newText)
            newText = re.sub('also','<i>also</i>',newText)
            self.ui.lGrammar.clear()
            self.ui.lGrammar.insertHtml(newText)
            theGrList = []
            theC2List = []
            theCfList = []
            for item in fullList:
                if 'also' in item:
                    subList = item.split(', ')
                    for subItem in subList:
                        theC2List.append(subItem)
                elif 'cf.' in item:
                    subList = item.split(', ')
                    for subItem in subList:
                        theCfList.append(subItem)
                else:
                    theGrList.append(item)
            if theCfList:
                theCfList[0] = re.sub('cf. ','',theCfList[0])                
            if theC2List:
                theC2List[0] = re.sub('also ','',theC2List[0])
            removeList = []
            for node in child.iter('Grm'):
                removeList.append(node)
            if len(removeList) != 0:
                for tag in removeList:
                    child.remove(tag)
            removeList = []
            for node in child.iter('C2'):
                removeList.append(node)
            if len(removeList) != 0:
                for tag in removeList:
                    child.remove(tag)
            removeList = []
            for node in child.iter('Cf'):
                removeList.append(node)
            if len(removeList) != 0:
                for tag in removeList:
                    child.remove(tag)                  
            if theGrList:
                for i in range(0,len(theGrList)):
                    child.insert(3+i,etree.Element('Grm'))
                i = 0
                for node in child.iter('Grm'):
                    node.text = formatHandler(theGrList[i])
                    i = i + 1
            if theC2List:
                elemList = list(child)
                elemList.reverse()
                i = 0
                for item in elemList:
                    if item.tag == 'Grm':
                        break
                    elif item.tag == 'IPA':
                        break
                    else:
                        i = i + 1
                i = len(elemList) - i
                for j in range(0,len(theC2List)):
                    child.insert(j+i,etree.Element('C2'))
                i = 0
                for node in child.iter('C2'):
                    node.text = formatHandler(theC2List[i])
                    i = i + 1
            if theCfList:
                elemList = list(child)
                elemList.reverse()
                i = 0
                for item in elemList:
                    if item.tag == 'C2':
                        break
                    elif item.tag == 'Grm':
                        break
                    elif item.tag == 'IPA':
                        break
                    else:
                        i = i + 1 
                i = len(elemList) - i
                for j in range(0,len(theCfList)):
                    child.insert(j+i,etree.Element('Cf'))
                i = 0
                for node in child.iter('Cf'):
                    node.text = formatHandler(theCfList[i])
                    i = i + 1

        elif fieldname == 'lSource':
            newContent = self.ui.lSource.toPlainText()
            child.set('Spkr',newContent)

        elif fieldname == 'lResearcher':
            newContent = self.ui.lResearcher.toPlainText()
            child.set('Rschr',newContent)
            
        elif fieldname == 'lDate':
            newContent = self.ui.lDate.toPlainText()
            child.set('Date',newContent)
            
        elif fieldname == 'lUpdated':
            newContent = self.ui.lUpdated.toPlainText()
            child.set('Update',newContent)
            
        elif fieldname == 'lConfirmed':
            newContent = self.ui.lConfirmed.toPlainText()
            child.set('Confirmed',newContent)

        elif fieldname == 'lNotes':
            newContent = ''
            if len(self.ui.lNotes.toPlainText()) != 0:
                theList = getCleanText(self.ui.lNotes.toHtml())
                for i in range(0, len(theList)):
                    if i != len(theList) - 1:
                        newContent = newContent + theList[i] + "\n"
                    else:
                        newContent = newContent + theList[i]
            comNode = child.find('Comments')
            if comNode != None:
                child.remove(comNode)
            if len(newContent) != 0:
                elemList = list(child)
                elemList.reverse()
                for i, item in enumerate(elemList):
                    if item.tag == 'Root':
                        break
                    elif item.tag == 'Drvn':
                        break
                    elif item.tag == 'Def':
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('Comments'))
                child.find('Comments').text = formatHandler(newContent)

        elif fieldname == 'lPrimaryIndex':
            newContent = self.ui.lPrimaryIndex.toPlainText()
            child.set('Index1',newContent)

        elif fieldname == 'lSecondaryIndex':
            newContent = self.ui.lSecondaryIndex.toPlainText()
            child.set('Index2',newContent)

        elif fieldname == 'lKeywordIndex':
            newContent = self.ui.lKeywordIndex.toPlainText()
            child.set('Kywd',newContent)

        #Examples
              
        elif fieldname == 'eLine':
            theList = getCleanText(self.ui.eLine.toHtml())
            newContent = theList[0]
            child.find('Line').text = formatHandler(newContent)
              
        elif fieldname == 'eL1Gloss':
            theList = getCleanText(self.ui.eL1Gloss.toHtml())
            newContent = theList[0]
            child.find('L1Gloss').text = formatHandler(newContent)
              
        elif fieldname == 'eL2Gloss':
            theList = getCleanText(self.ui.eL2Gloss.toHtml())
            newContent = theList[0]
            l2Node = child.find('L2Gloss')
            if l2Node != None:
                child.remove(l2Node)
            if len(newContent) != 0:
                elemList = list(child)
                elemList.reverse()
                for i, item in enumerate(elemList):
                    if item.tag == 'L1Gloss':
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('L2Gloss'))
                child.find('L2Gloss').text = formatHandler(newContent)
              
        elif fieldname == 'eNotes':
            newContent = ''
            if len(self.ui.eNotes.toPlainText()) != 0:
                theList = getCleanText(self.ui.eNotes.toHtml())
                for i in range(0, len(theList)):
                    if i != len(theList) - 1:
                        newContent = newContent + theList[i] + "\n"
                    else:
                        newContent = newContent + theList[i]
            comNode = child.find('Comments')
            if comNode != None:
                child.remove(comNode)
            if len(newContent) != 0:
                elemList = list(child)
                elemList.reverse()
                for i,item in enumerate(elemList):
                    if item.tag == 'L2Gloss':
                        break
                    elif item.tag == 'L1Gloss':
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('Comments'))
                child.find('Comments').text = formatHandler(newContent)
              
        elif fieldname == 'eKeywords':
            newContent = self.ui.eKeywords.toPlainText()
            child.set('Kywd',newContent)

        elif fieldname == 'eSource':
            newContent = self.ui.eSource.toPlainText()
            child.set('Spkr',newContent)
          
        elif fieldname == 'eResearcher':
            newContent = self.ui.eResearcher.toPlainText()
            child.set('Rschr',newContent)

        elif fieldname == 'eDate':
            newContent = self.ui.eDate.toPlainText()
            child.set('Date',newContent)

        #TEXTS
        elif fieldname == 'tNotes':
            newContent = ''
            if len(self.ui.tNotes.toPlainText()) != 0:
                theList = getCleanText(self.ui.tNotes.toHtml())
                for i in range(0, len(theList)):
                    if i != len(theList) - 1:
                        newContent = newContent + theList[i] + "\n"
                    else:
                        newContent = newContent + theList[i]
            comNode = child.find('Comments')
            if comNode != None:
                child.remove(comNode)
            if len(newContent) != 0:
                elemList = list(child)
                elemList.reverse()
                for i,item in enumerate(elemList):
                    if item.tag == 'Ln':
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('Comments'))
                child.find('Comments').text = formatHandler(newContent)
                
        elif fieldname == 'tTranscriber':
           newContent = self.ui.tTranscriber.toPlainText()
           child.set('Trns',newContent)

        elif fieldname == 'tSource':
           newContent = self.ui.tSource.toPlainText()
           child.set('Spkr',newContent)
          
        elif fieldname == 'tResearcher':
            newContent = self.ui.tResearcher.toPlainText()
            child.set('Rschr',newContent)

        elif fieldname == 'tDate':
            newContent = self.ui.tDate.toPlainText()
            child.set('Date',newContent)

        elif fieldname == 'tTitle':
            newContent = self.ui.tTitle.text()
            child.find('Title').text = newContent
            currentProxyIndex = self.ui.tTextNav.currentIndex()
            currentSourceIndex = self.ui.tTextNav.model().mapToSource(currentProxyIndex)
            self.ui.tTextNav.model().sourceModel().itemFromIndex(currentSourceIndex).setText(newContent)
            self.ui.tTextNav.model().setSortCaseSensitivity(0)
            self.ui.tTextNav.model().sort(0,QtCore.Qt.AscendingOrder)
            self.ui.tTextNav.scrollTo(self.ui.tTextNav.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)

        #DATASETS
        elif fieldname == 'dSource':
           newContent = self.ui.dSource.toPlainText()
           child.set('Spkr',newContent)
          
        elif fieldname == 'dResearcher':
            newContent = self.ui.dResearcher.toPlainText()
            child.set('Rschr',newContent)

        elif fieldname == 'dDate':
            newContent = self.ui.dDate.toPlainText()
            
        elif fieldname == 'dKeywords':
           newContent = self.ui.dKeywords.toPlainText()
           child.set('Kywd',newContent)
            
        elif fieldname == 'dNotes':
            newContent = ''
            if len(self.ui.dNotes.toPlainText()) != 0:
                theList = getCleanText(self.ui.dNotes.toHtml())
                for i in range(0, len(theList)):
                    if i != len(theList) - 1:
                        newContent = newContent + theList[i] + "\n"
                    else:
                        newContent = newContent + theList[i]
            comNode = child.find('Comments')
            if comNode != None:
                child.remove(comNode)
            if len(newContent) != 0:
                elemList = list(child)
                elemList.reverse()
                for i,item in enumerate(elemList):
                    if item.tag == 'Data':
                        break
                    elif item.tag == 'Ln':
                        break
                i = len(elemList) - i
                child.insert(i,etree.Element('Comments'))
                child.find('Comments').text = formatHandler(newContent)
                
        elif fieldname == 'dData':
            theList = getCleanText(self.ui.dData.toHtml())
            newContent = theList[0]
            for i in range(1,len(theList)):
                newContent = newContent + '\n' + theList[i]
            child.find('Data').text = formatHandler(newContent)
        
        elif fieldname == 'dTitle':
            newContent = self.ui.dTitle.text()
            child.find('Title').text = formatHandler(newContent)           
            currentProxyIndex = self.ui.dDataNav.currentIndex()
            currentSourceIndex = self.ui.dDataNav.model().mapToSource(currentProxyIndex)
            self.ui.dDataNav.model().sourceModel().itemFromIndex(currentSourceIndex).setText(newContent)
            self.ui.dDataNav.model().setSortCaseSensitivity(0)
            self.ui.dDataNav.model().sort(0,QtCore.Qt.AscendingOrder)
            self.ui.dDataNav.scrollTo(self.ui.dDataNav.currentIndex(), QtGui.QAbstractItemView.EnsureVisible)

    ######### end update XML ##########


    '''calls to event handlers, organized by Tab, Buttons first, then ListWidgets, ComboBoxes, and TextEdit fields'''

    '''HOME Tab'''

    '''ListWidgets'''

    def goToLxCard():
        pointer = self.ui.hLexNav.currentIndex()
        data = self.ui.hLexNav.currentIndex().data(32)
        self.ui.dataIndex.currentCard = data
        targetCard = self.ui.dataIndex.lexDict[data]
        cardLoader.loadLexCard(self, targetCard)
        self.ui.lLexNav.setCurrentIndex(pointer)
        self.ui.lLexNav.scrollTo(pointer, QtGui.QAbstractItemView.EnsureVisible)
        self.ui.dataIndex.unsavedEdit = 0
        self.ui.dataIndex.currentCard = data
        self.ui.tabWidget.setCurrentIndex(1)

    self.ui.hLexNav.clicked.connect(goToLxCard)
    
    def goToTxtCard():
      data = self.ui.hTextNav.currentIndex().data(32)
      self.ui.dataIndex.currentCard = data
      targetCard = self.ui.dataIndex.textDict[data]
      self.ui.tabWidget.setCurrentIndex(2)
      cardLoader.loadTextCard(self, targetCard)
      i = self.ui.hTextNav.currentIndex()
      self.ui.tTextNav.setCurrentIndex(i)
      self.ui.tTextNav.scrollTo(i, QtGui.QAbstractItemView.EnsureVisible)
      self.ui.dataIndex.unsavedEdit = 0

    self.ui.hTextNav.clicked.connect(goToTxtCard)
    
    def goToDataCard():
      data = self.ui.hDataNav.currentIndex().data(32)
      self.ui.dataIndex.currentCard = data
      targetCard = self.ui.dataIndex.dataDict[data]
      cardLoader.loadDataCard(self, targetCard)
      i = self.ui.hDataNav.currentIndex()
      self.ui.dDataNav.setCurrentIndex(i)
      self.ui.dDataNav.scrollTo(i, QtGui.QAbstractItemView.EnsureVisible)
      self.ui.tabWidget.setCurrentIndex(4)
      self.ui.dataIndex.unsavedEdit = 0

    self.ui.hDataNav.clicked.connect(goToDataCard)

    '''TextEdits'''
    
    dbTitle = self.ui.dataIndex.root.attrib.get('Dbase')
    self.ui.hTitle.setText(dbTitle)
    self.ui.hTitle.setAlignment(QtCore.Qt.AlignHCenter)
    self.filter = focusOutFilter(self.ui.hTitle)
    self.ui.hTitle.installEventFilter(self.filter)
    self.ui.hTitle.textChanged.connect(flagUnsavedEdits)

    lang = self.ui.dataIndex.root.attrib.get('Language')
    self.ui.hLanguage.setText(lang)
    self.filter = focusOutFilter(self.ui.hLanguage)
    self.ui.hLanguage.installEventFilter(self.filter)
    self.ui.hLanguage.textChanged.connect(flagUnsavedEdits)

    family = self.ui.dataIndex.root.attrib.get('Family')
    self.ui.hFamily.setText(family)
    self.filter = focusOutFilter(self.ui.hFamily)
    self.ui.hFamily.installEventFilter(self.filter)
    self.ui.hFamily.textChanged.connect(flagUnsavedEdits)
    
    population = self.ui.dataIndex.root.attrib.get('Population')
    self.ui.hPopulation.setText(population)
    self.filter = focusOutFilter(self.ui.hPopulation)
    self.ui.hPopulation.installEventFilter(self.filter)
    self.ui.hPopulation.textChanged.connect(flagUnsavedEdits)
    
    location = self.ui.dataIndex.root.attrib.get('Location')
    self.ui.hLocation.setText(location)
    self.filter = focusOutFilter(self.ui.hLocation)
    self.ui.hLocation.installEventFilter(self.filter)
    self.ui.hLocation.textChanged.connect(flagUnsavedEdits)
    
    iso = self.ui.dataIndex.root.attrib.get('ISO')
    self.ui.hISO.setText(iso)
    self.filter = focusOutFilter(self.ui.hISO)
    self.ui.hISO.installEventFilter(self.filter)
    self.ui.hISO.textChanged.connect(flagUnsavedEdits)
    
    '''LEXICON Tab'''

    '''Buttons'''
    self.ui.lBeginBtn.clicked.connect(btnCmds.firstLxCard)
    self.ui.lPrevBtn.clicked.connect(btnCmds.goPrevLx)
    self.ui.lRtnBtn.clicked.connect(btnCmds.btnBack)
    self.ui.lAdvancedSearch.clicked.connect(btnCmds.successMessage)
    self.ui.lNextBtn.clicked.connect(btnCmds.goNextLx)
    self.ui.lEndBtn.clicked.connect(btnCmds.lastLxCard)
    self.ui.lFwdBtn.clicked.connect(btnCmds.btnForward)
    self.ui.lSoundMetaBtn.clicked.connect(btnCmds.lMediaInfo)
    self.ui.lPlaySoundBtn.clicked.connect(btnCmds.lPlaySound)
    self.ui.lRadicalBtn.clicked.connect(btnCmds.addRoot)
    self.ui.lAddDerBtn.clicked.connect(btnCmds.addDrvn)
    self.ui.lRemoveDerBtn.clicked.connect(btnCmds.delDrvn)
    self.ui.lBreakLnkBtn.clicked.connect(btnCmds.removeRoot)
    if self.ui.dataIndex.root.attrib.get('Orth') == None:
        self.ui.lAutoBtn.setEnabled(0)
    if self.ui.dataIndex.root.attrib.get('lAuto') == 'on':
        self.ui.lAutoBtn.setChecked(1)
    else:
        self.ui.lAutoBtn.setChecked(0)
    self.ui.lAutoBtn.toggled.connect(btnCmds.toggleAuto)
    self.ui.lAddEgBtn.clicked.connect(btnCmds.lAddMedia)
    self.ui.lDelEgBtn.clicked.connect(btnCmds.lDelMedia)

    '''ListBoxes'''
    
    def goToLxCard2():
      data = self.ui.lLexNav.currentIndex().data(32)
      self.ui.dataIndex.currentCard = data
      targetCard = self.ui.dataIndex.lexDict[data]
      cardLoader.loadLexCard(self, targetCard)
      self.ui.dataIndex.unsavedEdit = 0

    self.ui.lLexNav.clicked.connect(goToLxCard2)

    def goToDerivation():
        data = self.ui.lDerivatives.currentItem().data(32)
        targetCard = self.ui.dataIndex.lexDict[data]
        cardLoader.loadLexCard(self, targetCard)
        self.ui.dataIndex.unsavedEdits = 0
        i = self.ui.lLexNav.findItems(targetCard.findtext('Orth'),QtCore.Qt.MatchExactly)
        self.ui.lLexNav.scrollToItem(i[0],QtGui.QAbstractItemView.PositionAtCenter) 
        for i in range(0,self.ui.lLexNav.count()):
            if self.ui.lLexNav.item(i).data(32) == data:
                theItem = i
                break                    
        self.ui.lLexNav.setCurrentRow(theItem)
        self.ui.lLexNav.scrollToItem(self.ui.lLexNav.currentItem(), QtGui.QAbstractItemView.PositionAtCenter)
      
    self.ui.lDerivatives.clicked.connect(goToDerivation)
    
    def goToBase():
        data = self.ui.lBase.currentItem().data(32)
        targetCard = self.ui.dataIndex.lexDict[data]
        cardLoader.loadLexCard(self, targetCard)
        self.ui.dataIndex.unsavedEdits = 0
        for i in range(0,self.ui.lLexNav.count()):
            if self.ui.lLexNav.item(i).data(32) == data:
                theItem = i
                break                    
        self.ui.lLexNav.setCurrentRow(theItem)
        self.ui.lLexNav.scrollToItem(self.ui.lLexNav.currentItem(), QtGui.QAbstractItemView.PositionAtCenter)
       
    self.ui.lBase.clicked.connect(goToBase)

    '''ComboBoxes'''

    def lRecChange():
        caller = self.ui.lRecordings
        mdField = self.ui.lSoundFileMeta
        ##might be nice to only update the field if the selection in the combobox has changed
        btnCmds.playSound(caller)
        for child in self.ui.dataIndex.root.iter('Media'):
            if child.attrib.get('MedID') == caller.itemData(caller.currentIndex(),35):
                speaker = child.attrib.get('Spkr')
                date = child.attrib.get('Date')
                mdField.setText(speaker + ' ' + date)
                break

    self.ui.lRecordings.activated.connect(lRecChange)

    '''TextEdits'''
        
    #Lexicographic info

    self.filter = focusOutFilter(self.ui.lOrthography)
    self.ui.lOrthography.installEventFilter(self.filter)
    self.ui.lOrthography.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.lPOS)
    self.ui.lPOS.installEventFilter(self.filter)
    self.ui.lPOS.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.lRegister)
    self.ui.lRegister.installEventFilter(self.filter)
    self.ui.lRegister.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.lIPA)
    self.ui.lIPA.installEventFilter(self.filter)
    self.ui.lIPA.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.lDialect)
    self.ui.lDialect.installEventFilter(self.filter)
    self.ui.lDialect.textChanged.connect(flagUnsavedEdits)
    self.filter = focusOutFilter(self.ui.lBrrw)
    self.ui.lBrrw.installEventFilter(self.filter)
    self.ui.lBrrw.textChanged.connect(flagUnsavedEdits)

    def dialectMenu(position):
      field = 'lDialect'
      cardLoader.openContextMenu(field, position)
      
    self.ui.lDialect.customContextMenuRequested.connect(dialectMenu)

    self.filter = focusOutFilter(self.ui.lLiteral)
    self.ui.lLiteral.installEventFilter(self.filter)
    self.ui.lLiteral.textChanged.connect(flagUnsavedEdits)

    #Metadata

    self.filter = focusOutFilter(self.ui.lSource)
    self.ui.lSource.installEventFilter(self.filter)
    self.ui.lSource.textChanged.connect(flagUnsavedEdits)
    
    self.filter = focusOutFilter(self.ui.lResearcher)
    self.ui.lResearcher.installEventFilter(self.filter)
    self.ui.lResearcher.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.lDate)
    self.ui.lDate.installEventFilter(self.filter)
    self.ui.lDate.textChanged.connect(flagUnsavedEdits)
    
    self.filter = focusOutFilter(self.ui.lUpdated)
    self.ui.lUpdated.installEventFilter(self.filter)
    self.ui.lUpdated.textChanged.connect(flagUnsavedEdits)
    
    self.filter = focusOutFilter(self.ui.lConfirmed)
    self.ui.lConfirmed.installEventFilter(self.filter)
    self.ui.lConfirmed.textChanged.connect(flagUnsavedEdits)

    #Grammar
    self.ui.lGrammar = GrmField()
    self.ui.lGrammar.setToolTip(QtGui.QApplication.translate("Fieldbook", "Grammatical information, comparisons, and cross-refs.\n"
    "Doubleclick to edit.", None, QtGui.QApplication.UnicodeUTF8))
    self.ui.superfluous3 = QtGui.QGroupBox(self.ui.lHeader)
    self.ui.superfluous3.setGeometry(QtCore.QRect(792, 27, 151, 100))
    self.ui.superfluous3.setStyleSheet("padding:0px; border:0px; margins:0px;")
    self.ui.superfluous4 = QtGui.QVBoxLayout()
    self.ui.superfluous4.setMargin(0)
    self.ui.superfluous3.setLayout(self.ui.superfluous4)
    self.ui.superfluous4.addWidget(self.ui.lGrammar)
    
    def grammarMenu(position):
      field = 'lGrammar'
      cardLoader.openContextMenu(field, position)

    self.ui.lGrammar.customContextMenuRequested.connect(grammarMenu)

    #Notes
    
    self.filter = focusOutFilter(self.ui.lNotes)
    self.ui.lNotes.installEventFilter(self.filter)
    self.ui.lNotes.textChanged.connect(flagUnsavedEdits)

    #Indices
    
    self.filter = focusOutFilter(self.ui.lPrimaryIndex)
    self.ui.lPrimaryIndex.installEventFilter(self.filter)
    self.ui.lPrimaryIndex.textChanged.connect(flagUnsavedEdits)
    
    self.filter = focusOutFilter(self.ui.lSecondaryIndex)
    self.ui.lSecondaryIndex.installEventFilter(self.filter)
    self.ui.lSecondaryIndex.textChanged.connect(flagUnsavedEdits)
    
    self.filter = focusOutFilter(self.ui.lKeywordIndex)
    self.ui.lKeywordIndex.installEventFilter(self.filter)
    self.ui.lKeywordIndex.textChanged.connect(flagUnsavedEdits)
    
    '''definitions tables'''
    
    self.ui.lL1Definition = DefTable()
    superfluous = QtGui.QVBoxLayout()
    superfluous.addWidget(self.ui.lL1Definition)
    self.ui.lL1Box.setLayout(superfluous)
    self.ui.lL2Definition = DefTable()
    superfluous2 = QtGui.QVBoxLayout()
    superfluous2.addWidget(self.ui.lL2Definition)
    self.ui.lL2Box.setLayout(superfluous2)
    self.ui.lL1Definition.setToolTip(QtGui.QApplication.translate("Fieldbook", "Definitions in primary working language. \n"
    "Doubleclick to edit, click on example to go to analysis.", None, QtGui.QApplication.UnicodeUTF8))
    self.ui.lL2Definition.setToolTip(QtGui.QApplication.translate("Fieldbook", "Definitions in secondary working language. \n"
    "Doubleclick to edit, click on example to go to analysis.", None, QtGui.QApplication.UnicodeUTF8))

    def L1Menu(position):
      field = 'lL1Definition'
      cardLoader.openContextMenu(field, position)

    self.ui.lL1Definition.customContextMenuRequested.connect(L1Menu)
    
    def L2Menu(position):
      field = 'lL2Definition'
      cardLoader.openContextMenu(field, position)
    
    self.ui.lL2Definition.customContextMenuRequested.connect(L2Menu)

    '''TEXTS Tab'''
    
    '''Buttons'''
    
    self.ui.tBeginBtn.clicked.connect(btnCmds.firstTxtCard)
    self.ui.tPrevBtn.clicked.connect(btnCmds.goPrevTxt)
    self.ui.tRtnBtn.clicked.connect(btnCmds.btnBack)
    self.ui.tAdvancedSearch.clicked.connect(btnCmds.successMessage)
    self.ui.tNextBtn.clicked.connect(btnCmds.goNextTxt)
    self.ui.tEndBtn.clicked.connect(btnCmds.lastTxtCard)
    self.ui.tFwdBtn.clicked.connect(btnCmds.btnForward)
    self.ui.tSoundMetaBtn.clicked.connect(btnCmds.tMediaInfo)
    self.ui.tPlaySoundBtn.clicked.connect(btnCmds.tPlaySound)
    self.ui.tNewLineBtn.clicked.connect(btnCmds.tNewLine)
    self.ui.tSplitLineBtn.clicked.connect(btnCmds.tSplitLine)
    self.ui.tRemoveLineBtn.clicked.connect(btnCmds.tRemoveLine)
    self.ui.tAnalyzeBtn.clicked.connect(btnCmds.tAnalyzeLine)
    self.ui.tNewLineBtn.setEnabled(0)
    self.ui.tSplitLineBtn.setEnabled(0)
    self.ui.tRemoveLineBtn.setEnabled(0)
    self.ui.tAnalyzeBtn.setEnabled(0)
    self.ui.tAddEgBtn.clicked.connect(btnCmds.tAddMedia)
    self.ui.tDelEgBtn.clicked.connect(btnCmds.tDelMedia)   
    self.ui.tCopyLineBtn.clicked.connect(btnCmds.tCopyLine)

    '''ListWidgets'''
    
    def goToTxtCard2():
      data = self.ui.tTextNav.currentIndex().data(32)
      self.ui.dataIndex.currentCard = data
      targetCard = self.ui.dataIndex.textDict[data]
      cardLoader.loadTextCard(self, targetCard)
      self.ui.dataIndex.unsavedEdit = 0

    self.ui.tTextNav.clicked.connect(goToTxtCard2)

    '''ComboBoxes'''

    def tRecChange():
        caller = self.ui.tRecordings
        mdField = self.ui.tSoundFileMeta
        ##might be nice to only update the field if the selection in the combobox has changed
        btnCmds.playSound(caller)
        for child in self.ui.dataIndex.root.iter('Media'):
            if child.attrib.get('MedID') == caller.itemData(caller.currentIndex(),35):
                speaker = child.attrib.get('Spkr')
                date = child.attrib.get('Date')
                mdField.setText(speaker + ' ' + date)
                break

    self.ui.tRecordings.activated.connect(tRecChange)

    '''TextEdits'''
    
    self.filter = focusOutFilter(self.ui.tSource)
    self.ui.tSource.installEventFilter(self.filter)
    self.ui.tSource.textChanged.connect(flagUnsavedEdits)
    
    self.filter = focusOutFilter(self.ui.tResearcher)
    self.ui.tResearcher.installEventFilter(self.filter)
    self.ui.tResearcher.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.tDate)
    self.ui.tDate.installEventFilter(self.filter)
    self.ui.tDate.textChanged.connect(flagUnsavedEdits)
    
    self.filter = focusOutFilter(self.ui.tUpdated)
    self.ui.tUpdated.installEventFilter(self.filter)
    self.ui.tUpdated.textChanged.connect(flagUnsavedEdits)
    
    self.filter = focusOutFilter(self.ui.tTranscriber)
    self.ui.tTranscriber.installEventFilter(self.filter)
    self.ui.tTranscriber.textChanged.connect(flagUnsavedEdits)
   
    self.filter = focusOutFilter(self.ui.tNotes)
    self.ui.tNotes.installEventFilter(self.filter)
    self.ui.tNotes.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.tTitle)
    self.ui.tTitle.installEventFilter(self.filter)
    self.ui.tTitle.textChanged.connect(flagUnsavedEdits)


    '''EXAMPLES Tab'''

    '''load first example card'''
    
    self.ui.eAbbreviations = QtGui.QTableWidget(self.ui.eAbbrBox)
    self.ui.eAbbreviations.setGeometry(15,34,230,466)
    delegate = HTMLDelegate()
    self.ui.eAbbreviations.setItemDelegate(delegate)
    self.ui.eAbbreviations.horizontalHeader().setEnabled(0)
    self.ui.eAbbreviations.verticalHeader().setEnabled(0)
    self.ui.eAbbreviations.verticalHeader().hide()
    self.ui.eAbbreviations.horizontalHeader().hide()
    self.ui.eAbbreviations.setShowGrid(0)
    self.ui.eAbbreviations.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
    self.ui.eAbbreviations.setStyleSheet("selection-background-color: #E6E6E6;")
    self.ui.eAbbreviations.setColumnCount(1)

    def makeAbbrList():
        self.ui.eAbbreviations.setRowCount(0)
        for child in self.ui.dataIndex.root.iter('Abbr'):
            abbrev = child.attrib.get('Abv').swapcase()
            itemText = '<small>' + abbrev + '</small>&emsp;‘' + child.attrib.get('Term') + '’'
            try:
                form = child.attrib.get('Form')
                itemText += ' (' + form + ')'
            except AttributeError:
                pass
            except TypeError:
                pass
            newItem = QtGui.QTableWidgetItem(1001)
            newItem.setData(35,child.attrib.get('ACode'))
            newItem.setData(36,child)
            newItem.setText(itemText)
            newItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            nextRow = self.ui.eAbbreviations.rowCount()
            self.ui.eAbbreviations.setRowCount(nextRow+1)
            self.ui.eAbbreviations.setItem(nextRow,0,newItem)
            self.ui.eAbbreviations.setRowHeight(nextRow,20)
        self.ui.eAbbreviations.resizeColumnToContents(0)
        self.ui.eAbbreviations.sortItems(0,QtCore.Qt.AscendingOrder)

    makeAbbrList()

    '''Buttons'''
    
    self.ui.eBeginBtn.clicked.connect(btnCmds.firstEgCard)
    self.ui.ePrevBtn.clicked.connect(btnCmds.goPrevEg)
    self.ui.eRtnBtn.clicked.connect(btnCmds.btnBack)
    self.ui.eAdvancedSearch.clicked.connect(btnCmds.successMessage)
    self.ui.eNextBtn.clicked.connect(btnCmds.goNextEg)
    self.ui.eEndBtn.clicked.connect(btnCmds.lastEgCard)
    self.ui.eFwdBtn.clicked.connect(btnCmds.btnForward)
    self.ui.eSoundMetaBtn.clicked.connect(btnCmds.eMediaInfo)
    self.ui.ePlaySoundBtn.clicked.connect(btnCmds.ePlaySound)
    self.ui.eAddExampleBtn.clicked.connect(btnCmds.eAdd2Lex)
    self.ui.eLocateBtn.clicked.connect(btnCmds.eLocateEg)
    self.ui.eSplitBtn.clicked.connect(btnCmds.eSplitEg)
    self.ui.eDeleteBtn.clicked.connect(btnCmds.eRemoveColumn)
    self.ui.eMakeIndexBtn.clicked.connect(btnCmds.successMessage)
    self.ui.eUpdateBtn.clicked.connect(btnCmds.eUpdateText)
    self.ui.eAddAbbrBtn.clicked.connect(btnCmds.addAbbr)
    self.ui.eDelAbbrBtn.clicked.connect(btnCmds.delAbbr)
    self.ui.eEditAbbrBtn.clicked.connect(btnCmds.editAbbr)
    self.ui.eAddEgBtn.clicked.connect(btnCmds.eAddMedia)
    self.ui.eDelEgBtn.clicked.connect(btnCmds.eDelMedia)
    self.ui.eCopyLineBtn.clicked.connect(btnCmds.eCopyLine)
    if self.ui.dataIndex.root.attrib.get('eParse') == 'on':
        self.ui.eAutoParsingBtn.setChecked(1)
    else:
        self.ui.eAutoParsingBtn.setChecked(0)
    self.ui.eAutoParsingBtn.toggled.connect(btnCmds.toggleParse)
    
    '''ComboBoxes'''
    
    def eRecChange():
        caller = self.ui.eRecordings
        mdField = self.ui.eSoundFileMeta
        ##might be nice to only update the field if the selection in the combobox has changed
        btnCmds.playSound(caller)
        for child in self.ui.dataIndex.root.iter('Media'):
            if child.attrib.get('MedID') == caller.itemData(caller.currentIndex(),35):
                speaker = child.attrib.get('Spkr')
                date = child.attrib.get('Date')
                mdField.setText(speaker + ' ' + date)
                break

    self.ui.eRecordings.activated.connect(eRecChange)

    '''TextEdits'''
    
    self.filter = focusOutFilter(self.ui.eLine)
    self.ui.eLine.installEventFilter(self.filter)
    self.ui.eLine.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eL1Gloss)
    self.ui.eL1Gloss.installEventFilter(self.filter)
    self.ui.eL1Gloss.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eL2Gloss)
    self.ui.eL2Gloss.installEventFilter(self.filter)
    self.ui.eL2Gloss.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eNotes)
    self.ui.eNotes.installEventFilter(self.filter)
    self.ui.eNotes.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eKeywords)
    self.ui.eKeywords.installEventFilter(self.filter)
    self.ui.eKeywords.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eSource)
    self.ui.eSource.installEventFilter(self.filter)
    self.ui.eSource.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eResearcher)
    self.ui.eResearcher.installEventFilter(self.filter)
    self.ui.eResearcher.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eDate)
    self.ui.eDate.installEventFilter(self.filter)
    self.ui.eDate.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eUpdated)
    self.ui.eUpdated.installEventFilter(self.filter)
    self.ui.eUpdated.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eSourceText)
    self.ui.eSourceText.installEventFilter(self.filter)
    self.ui.eSourceText.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.eTimeCode)
    self.ui.eTimeCode.installEventFilter(self.filter)
    self.ui.eTimeCode.textChanged.connect(flagUnsavedEdits)
    
    '''create table for analyses'''
    self.ui.eAnalysis = EgTable(self.ui.eExScrollArea)
    self.ui.eAnalysis.setGeometry(0,60,1900,212)
    
    '''DATASETS Tab'''

    '''Buttons'''
    
    self.ui.dBeginBtn.clicked.connect(btnCmds.firstDsetCard)
    self.ui.dPrevBtn.clicked.connect(btnCmds.goPrevDset)
    self.ui.dRtnBtn.clicked.connect(btnCmds.btnBack)
    self.ui.dAdvancedSearch.clicked.connect(btnCmds.successMessage)
    self.ui.dNextBtn.clicked.connect(btnCmds.goNextDset)
    self.ui.dEndBtn.clicked.connect(btnCmds.lastDsetCard)
    self.ui.dFwdBtn.clicked.connect(btnCmds.btnForward)
    self.ui.dSoundMetaBtn.clicked.connect(btnCmds.dMediaInfo)
    self.ui.dPlaySoundBtn.clicked.connect(btnCmds.dPlaySound)
    self.ui.dAddEgBtn.clicked.connect(btnCmds.dAddMedia)
    self.ui.dDelEgBtn.clicked.connect(btnCmds.dDelMedia)
    
    '''ComboBoxes'''

    def dRecChange():
        caller = self.ui.dRecordings
        mdField = self.ui.dSoundFileMeta
        ##might be nice to only update the field if the selection in the combobox has changed
        btnCmds.playSound(caller)
        for child in self.ui.dataIndex.root.iter('Media'):
            if child.attrib.get('MedID') == caller.itemData(caller.currentIndex(),35):
                speaker = child.attrib.get('Spkr')
                date = child.attrib.get('Date')
                mdField.setText(speaker + ' ' + date)
                break

    self.ui.dRecordings.activated.connect(dRecChange)

    '''ListWidgets'''
    
    def goToDataCard2():
      data = self.ui.dDataNav.currentIndex().data(32)
      self.ui.dataIndex.currentCard = data
      targetCard = self.ui.dataIndex.dataDict[data]
      cardLoader.loadDataCard(self, targetCard)
      self.ui.tabWidget.setCurrentIndex(4)
      self.ui.dataIndex.unsavedEdit = 0

    self.ui.dDataNav.clicked.connect(goToDataCard2)

    '''TextEdits'''
    
    self.filter = focusOutFilter(self.ui.dSource)
    self.ui.dSource.installEventFilter(self.filter)
    self.ui.dSource.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.dResearcher)
    self.ui.dResearcher.installEventFilter(self.filter)
    self.ui.dResearcher.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.dDate)
    self.ui.dDate.installEventFilter(self.filter)
    self.ui.dDate.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.dKeywords)
    self.ui.dKeywords.installEventFilter(self.filter)
    self.ui.dKeywords.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.dNotes)
    self.ui.dNotes.installEventFilter(self.filter)
    self.ui.dNotes.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.dData)
    self.ui.dData.installEventFilter(self.filter)
    self.ui.dData.textChanged.connect(flagUnsavedEdits)

    self.filter = focusOutFilter(self.ui.dTitle)
    self.ui.dTitle.installEventFilter(self.filter)
    self.ui.dTitle.textChanged.connect(flagUnsavedEdits)


    '''CONCORDANCES Tab'''

    '''Buttons'''
    
    self.ui.cLoadPrevBtn.clicked.connect(btnCmds.successMessage)
    self.ui.cSaveResultsBtn.clicked.connect(btnCmds.successMessage)
    self.ui.cClearResultsBtn.clicked.connect(btnCmds.successMessage)
   
    '''ListBoxes'''
    
    ##fill boxes listview with stuff to play with
    for i in range (1,101):
      self.ui.cSearchResults.addItem("Hit %i" % i)


    '''METADATA Tab'''

    '''Consultants sub-tab'''

    def fillSpForm():
        self.ui.mSpTable.selectRow(self.ui.mSpTable.currentRow())
        u = self.ui.mSpTable.currentRow()
        self.ui.mSCode.clear()
        self.ui.mSpeaker.clear()
        self.ui.mBirthday.clear()
        self.ui.mBirthplace.clear()
        self.ui.mInfo.clear()
        self.ui.mSCode.setHtml(self.ui.mSpTable.item(u,0).text())
        self.ui.mSpeaker.setHtml(self.ui.mSpTable.item(u,1).text())
        self.ui.mBirthday.setHtml(self.ui.mSpTable.item(u,2).text())
        self.ui.mBirthplace.setHtml(self.ui.mSpTable.item(u,3).text())
        self.ui.mInfo.setHtml(self.ui.mSpTable.item(u,4).text())
        self.ui.mSpAddBtn.setEnabled(0)
        self.ui.mSpDelBtn.setEnabled(1)
        self.ui.mSpUpdateBtn.setEnabled(1)
        self.ui.mSCode.setReadOnly(1)

    self.ui.mSpTable = QtGui.QTableWidget(self.ui.mConsultantsTab)
    self.ui.mSpTable.setGeometry(15,0,500,272)
    self.ui.mSpTable.setItemDelegate(delegate)
    self.ui.mSpTable.horizontalHeader().setEnabled(0)
    self.ui.mSpTable.verticalHeader().setEnabled(0)
    self.ui.mSpTable.verticalHeader().hide()
    self.ui.mSpTable.horizontalHeader().hide()
    self.ui.mSpTable.setShowGrid(0)
    self.ui.mSpTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
    self.ui.mSpTable.setStyleSheet("selection-background-color: #E6E6E6;")
    self.ui.mSpTable.setColumnCount(5)
    self.ui.mSpTable.itemClicked.connect(fillSpForm)

    def fillConsultantTable():
        self.ui.mSpTable.setRowCount(0)
        for child in self.ui.dataIndex.root.iter('Speaker'):
            name = child.find('Name').text
            code = child.attrib.get('SCode')
            try:
                birthday = child.find('Birthdate').text
            except AttributeError:
                birthday = None
            try:
                place = child.find('Place').text
            except AttributeError:
                place = None
            try:
                info = child.find('Info').text
            except AttributeError:
                info = None
            dataList = [code,name,birthday,place,info]
            nextRow = self.ui.mSpTable.rowCount()
            self.ui.mSpTable.setRowCount(nextRow+1)
            self.ui.mSpTable.setRowHeight(nextRow,20)
            for i in range(0,5):
                newItem = QtGui.QTableWidgetItem(1001)
                if dataList[i] != None:
                    itemText = dataList[i]
                    newItem.setText(itemText)
                newItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                self.ui.mSpTable.setItem(nextRow,i,newItem)
            self.ui.mSpTable.item(nextRow,0).setData(36,child)
        for j in range(0,self.ui.mSpTable.columnCount()-1):
            self.ui.mSpTable.resizeColumnToContents(j)

    fillConsultantTable()
    self.ui.mSpTable.sortItems(0,QtCore.Qt.AscendingOrder)

    '''researchers sub-tab'''

    def fillRForm():
        self.ui.mRTable.selectRow(self.ui.mRTable.currentRow())
        u = self.ui.mRTable.currentRow()
        self.ui.mRCode.clear()
        self.ui.mResearcher.clear()
        self.ui.mAffiliation.clear()
        self.ui.mRInfo.clear()
        self.ui.mRCode.setHtml(self.ui.mRTable.item(u,0).text())
        self.ui.mResearcher.setHtml(self.ui.mRTable.item(u,1).text())
        self.ui.mAffiliation.setHtml(self.ui.mRTable.item(u,3).text())
        self.ui.mRInfo.setHtml(self.ui.mRTable.item(u,4).text())
        self.ui.mRAddBtn.setEnabled(0)
        self.ui.mRDelBtn.setEnabled(1)
        self.ui.mRCode.setReadOnly(1)
        self.ui.mRUpdateBtn.setEnabled(1)
        y = self.ui.mPrivilegesBox.findText(self.ui.mRTable.item(u,0).data(40))
        if y != -1:
            self.ui.mPrivilegesBox.setCurrentIndex(y)
        elif y == 'None':
            self.ui.mPrivilegesBox.setCurrentIndex(-1)
        else:
            self.ui.mPrivilegesBox.setCurrentIndex(-1)

    self.ui.mRTable = QtGui.QTableWidget(self.ui.mResearchersTab)
    self.ui.mRTable.setGeometry(15,0,500,272)
    self.ui.mRTable.setItemDelegate(delegate)
    self.ui.mRTable.horizontalHeader().setEnabled(0)
    self.ui.mRTable.verticalHeader().setEnabled(0)
    self.ui.mRTable.verticalHeader().hide()
    self.ui.mRTable.horizontalHeader().hide()
    self.ui.mRTable.setShowGrid(0)
    self.ui.mRTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
    self.ui.mRTable.setStyleSheet("selection-background-color: #E6E6E6;")
    self.ui.mRTable.setColumnCount(5)
    self.ui.mRTable.itemClicked.connect(fillRForm)

    def fillRTable():
        self.ui.mRTable.setRowCount(0)
        for child in self.ui.dataIndex.root.iter('Rschr'):
            name = child.find('Name').text
            code = child.attrib.get('RCode')
            try:
                level = child.attrib.get('Level')
            except AttributeError:
                level = None
            try:
                affiliation = child.find('Affiliation').text
            except AttributeError:
                affiliation = None
            try:
                info = child.find('Info').text
            except AttributeError:
                info = None
            dataList = [code,name,level,affiliation,info]
            nextRow = self.ui.mRTable.rowCount()
            self.ui.mRTable.setRowCount(nextRow+1)
            self.ui.mRTable.setRowHeight(nextRow,20)
            for i in range(0,5):
                newItem = QtGui.QTableWidgetItem(1001)
                if dataList[i] != None:
                    itemText = dataList[i]
                    newItem.setText(itemText)
                newItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                self.ui.mRTable.setItem(nextRow,i,newItem)
            self.ui.mRTable.item(nextRow,0).setData(36,child)
            self.ui.mRTable.item(nextRow,0).setData(40,level)
        for j in range(0,self.ui.mRTable.columnCount()-1):
            self.ui.mRTable.resizeColumnToContents(j)
            if self.ui.mRTable.columnWidth(j) > 165:
                self.ui.mRTable.setColumnWidth(j,165)
        self.ui.mRTable.resizeColumnToContents(self.ui.mRTable.columnCount()-1)

    fillRTable()
    self.ui.mRTable.sortItems(0,QtCore.Qt.AscendingOrder)

    '''media sub-tab'''

    def selectMRow():
        if self.ui.mMediaTable.currentColumn() == 3:
            btnCmds.mMediaInfo()
        self.ui.mMediaTable.selectRow(self.ui.mMediaTable.currentRow())
    
    self.ui.mMediaTable = QtGui.QTableWidget(self.ui.mMediaBox)
    self.ui.mMediaTable.setGeometry(15,33,328,556)
    self.ui.mMediaTable.horizontalHeader().setEnabled(0)
    self.ui.mMediaTable.verticalHeader().setEnabled(0)
    self.ui.mMediaTable.verticalHeader().hide()
    self.ui.mMediaTable.horizontalHeader().hide()
    self.ui.mMediaTable.setShowGrid(0)
    self.ui.mMediaTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
    self.ui.mMediaTable.setStyleSheet("selection-background-color: #E6E6E6;")
    self.ui.mMediaTable.setColumnCount(4)
    self.ui.mMediaTable.setAlternatingRowColors(1)
    self.ui.mMediaTable.itemClicked.connect(selectMRow)

    def fillMediaTable():
        self.ui.mMediaTable.setRowCount(0)
        self.ui.mMediaTable.setColumnWidth(0,220)
        self.ui.mMediaTable.setColumnWidth(1,30)
        self.ui.mMediaTable.setColumnWidth(2,40)
        self.ui.mMediaTable.setColumnWidth(3,25)
        for item in self.ui.dataIndex.mediaDict:
            mediaElement = self.ui.dataIndex.mediaDict[item]
            file = mediaElement.attrib.get('Filename')
            try:
                speaker = mediaElement.attrib.get('Spkr')
            except AttributeError:
                speaker = None
            try:
                researcher = mediaElement.attrib.get('Rschr')
            except AttributeError:
                researcher = None
            dataList = [file,speaker,researcher]
            nextRow = self.ui.mMediaTable.rowCount()
            self.ui.mMediaTable.setRowCount(nextRow+1)
            self.ui.mMediaTable.setRowHeight(nextRow,20)
            for i in range(0,len(dataList)):
                newItem = QtGui.QTableWidgetItem(1001)
                if dataList[i] != None:
                    itemText = dataList[i]
                    newItem.setText(itemText)
                    newItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.ui.mMediaTable.setItem(nextRow,i,newItem)
            self.ui.mMediaTable.item(nextRow,0).setData(36,mediaElement)
            newItem = QtGui.QTableWidgetItem(1001)
            newItem.setIcon(QtGui.QIcon(":/new/infoBtn.png"))
            self.ui.mMediaTable.setItem(nextRow,3,newItem)        

    fillMediaTable()
    self.ui.mMediaTable.sortItems(0,QtCore.Qt.AscendingOrder)
    
    '''orthographies sub-tab'''
    
    self.ui.oList.setColumnWidth(0,80)    
    self.ui.oList.setColumnWidth(1,58)    
    self.ui.oList.verticalHeader().hide()
    self.ui.oList.setAlternatingRowColors(1)
    self.ui.oList.setStyleSheet("selection-background-color: #E6E6E6;")
    if self.ui.dataIndex.root.find('Orthographies') != None:
        orthList = self.ui.dataIndex.root.findall('Orthographies/Map')
        self.ui.oList.setRowCount(len(orthList))
        for i,item in enumerate(orthList):
            name = item.attrib.get('Name')
            kind = item.attrib.get('Type')
            newOrth = QtGui.QTableWidgetItem(1001)
            newType = QtGui.QTableWidgetItem(1001)
            newOrth.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            newType.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            newOrth.setText(name)
            newType.setText(kind)
            self.ui.oList.setItem(i,0,newOrth)
            self.ui.oList.setItem(i,1,newType)
            self.ui.oList.item(i,0).setData(36,item)
            self.ui.oList.setRowHeight(i,20)    

        if self.ui.dataIndex.root.attrib.get('Orth') != None:
            for i,item in enumerate(orthList):
                if item.attrib.get('Name') == self.ui.dataIndex.root.attrib.get('Orth'):
                    node = self.ui.oList.item(i,0).data(36)
                    order = node.text
                    self.ui.oOrder.setPlainText(order)
                    self.ui.oList.selectRow(i)
    else:
        self.ui.oDeleteBtn.setEnabled(0)
        self.ui.oUpdateBtn.setEnabled(0)
        self.ui.oClearTransformBtn.setEnabled(0)   
            
    def selectORow():
        theRow = self.ui.oList.currentRow()
        node = self.ui.oList.item(theRow,0).data(36)
        order = node.text
        self.ui.oOrder.setPlainText(order)
        self.ui.oList.selectRow(theRow)
        self.ui.oDeleteBtn.setEnabled(1)
        self.ui.oUpdateBtn.setEnabled(1)
        self.ui.oClearTransformBtn.setEnabled(1)   
    
    self.ui.oList.itemClicked.connect(selectORow)

    '''Buttons'''
    '''consultants sub-tab'''
    
    self.ui.mSpDelBtn.setEnabled(0)
    self.ui.mSpUpdateBtn.setEnabled(0)
    self.ui.mSpUpdateBtn.clicked.connect(btnCmds.mSpUpdate)
    self.ui.mSpAddBtn.clicked.connect(btnCmds.mSpAdd)
    self.ui.mSpDelBtn.clicked.connect(btnCmds.mSpDel)    
    self.ui.mSpClearBtn.clicked.connect(btnCmds.mSpClear)
    
    '''researchers sub-tab'''
    
    self.ui.mRDelBtn.setEnabled(0)
    self.ui.mRUpdateBtn.setEnabled(0)
    self.ui.mRUpdateBtn.clicked.connect(btnCmds.mRUpdate)
    self.ui.mRAddBtn.clicked.connect(btnCmds.mRAdd)
    self.ui.mRDelBtn.clicked.connect(btnCmds.mRDel)    
    self.ui.mRClearBtn.clicked.connect(btnCmds.mRClear)

    '''media box'''

    self.ui.mPlaySoundBtn.clicked.connect(btnCmds.mPlaySound)
    self.ui.mChooseDirBtn.clicked.connect(btnCmds.mChooseDir)
    self.ui.mAddMediaBtn.clicked.connect(btnCmds.mAddMedia)
    self.ui.mDelMediaBtn.clicked.connect(btnCmds.mDelMedia)
    
    '''orthographies sub-tab'''

    self.ui.oClearTransformBtn.clicked.connect(btnCmds.oClearTransform)   
    self.ui.oDeleteBtn.clicked.connect(btnCmds.oDelete)   
    self.ui.oNewBtn.clicked.connect(btnCmds.oNew)   
    self.ui.oUpdateBtn.clicked.connect(btnCmds.oUpdate)   
    self.ui.oClearTestBtn.clicked.connect(btnCmds.oClearTest)   
    self.ui.oRandomBtn.clicked.connect(btnCmds.oRandom)   
    self.ui.oTestBtn.clicked.connect(btnCmds.oTest)   
    self.ui.oNumberBox.valueChanged.connect(btnCmds.oNumber)   

    '''Combo boxes'''

    levelList = ['Admin','Editor','Output','Read only','None']
    self.ui.mPrivilegesBox.insertItems(-1,levelList)
    self.ui.mPrivilegesBox.setCurrentIndex(-1)
    
    '''MENUBAR'''

    ###### Menu action definitions #####
    
    def okToContinue():
        if self.ui.dataIndex.unsavedEdit == 1:
             msgbox = QtGui.QMessageBox()
             msgbox.setText("Any unsaved changes will be lost.")
             msgbox.setInformativeText("Do you want to save changes?")
             msgbox.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
             msgbox.setDefaultButton(QtGui.QMessageBox.Save)
             reply = msgbox.exec_()
             if reply == QtGui.QMessageBox.Cancel:
               return False
             elif reply == QtGui.QMessageBox.Yes:
               return saveDb()
             return True
        else:
             return True

    '''Application menu items'''
    
    def showAbout():
        Fieldbook.aboutBox = QtGui.QMessageBox()
        details = open("GNU.txt", "r", encoding="UTF-8").read()
        Fieldbook.aboutBox.setDetailedText(details)
        Fieldbook.aboutBox.setStandardButtons(QtGui.QMessageBox.Ok)
        Fieldbook.aboutBox.setDefaultButton(QtGui.QMessageBox.Ok)
        Fieldbook.aboutBox.setText("<center><b>Electronic Fieldbook</b></center>")
        Fieldbook.aboutBox.setInformativeText("<center><small>© 2011, David Beck</small></center>"
                                    "<p>This program is free software; you can redistribute it "
                                    "and/or modify it under the terms of the GNU General Public "
                                    "License as published by the Free Software Foundation, "
                                    "given below.</p>"
                                    "<p>This program is distributed in the hope "
                                    "that it will be useful, but <i>without any warranty</i>; "
                                    "without even the implied warranty of <i>merchant ability "
                                    "or fitness for a particular purpose</i>. See the GNU General "
                                    "Public License below for more details.</p>")
        Fieldbook.aboutBox.exec_()

    self.ui.actionAbout.triggered.connect(showAbout)
    
    '''File Menu items'''
    
    '''New file'''
    def newDb():
      #print(self.ui.dataIndex.sourceFile)
      if self.ui.dataIndex.sourceFile:
        if okToContinue():
          print("new file")
      #showAbout()
     
    self.ui.actionNew.triggered.connect(newDb)          
           
    '''Open'''
    
    def openDb():
      self.ui.tabWidget.setCurrentIndex(0)
      currentFile = self.ui.dataIndex.sourceFile
      if currentFile:
          if not okToContinue():
              return
      parent = None
      fname = QtGui.QFileDialog.getOpenFileName(parent, "Open...")
      if fname:
          self.ui.dataIndex.xmltree = etree.parse(fname)
          self.ui.dataIndex.root = self.ui.dataIndex.xmltree.getroot()
          #rebuild the window contents using the new file
          self.ui.dataIndex.lexDict.clear()
          self.ui.dataIndex.textDict.clear()
          self.ui.dataIndex.dataDict.clear()
          self.ui.hLexNav.clear()
          self.ui.lLexNav.clear()
          self.ui.hTextNav.clear()
          self.ui.tTextNav.clear()      
          self.ui.hDataNav.clear()
          self.ui.dDataNav.clear()
          navLexEntry()
          navText()
          navDset()
          makeAbbrList()
          fillConsultantTable()
          self.ui.tabWidget.setTabEnabled(1,1)
          self.ui.tabWidget.setTabEnabled(2,1)
          self.ui.tabWidget.setTabEnabled(3,1)
          self.ui.tabWidget.setTabEnabled(4,1)
          self.ui.tabWidget.setTabEnabled(5,1)
          self.ui.tabWidget.setTabEnabled(6,1)
          self.ui.tabWidget.setTabEnabled(7,1)
          self.ui.tabWidget.setTabEnabled(8,1)
          dbTitle = self.ui.dataIndex.root.attrib.get('Dbase')
          self.ui.hTitle.setText(dbTitle)
          self.ui.hTitle.setAlignment(QtCore.Qt.AlignHCenter)
          lang = self.ui.dataIndex.root.attrib.get('Language')
          self.ui.hLanguage.setText(lang)
          family = self.ui.dataIndex.root.attrib.get('Family')
          self.ui.hFamily.setText(family)
          population = self.ui.dataIndex.root.attrib.get('Population')
          self.ui.hPopulation.setText(population)
          location = self.ui.dataIndex.root.attrib.get('Location')
          self.ui.hLocation.setText(location)
          iso = self.ui.dataIndex.root.attrib.get('ISO')
          self.ui.hISO.setText(iso)   
      self.ui.dataIndex.recentFile = updateRecentFile(self.ui.dataIndex.recentFile, currentFile)
      self.ui.dataIndex.sourceFile = fname
      self.ui.dataIndex.unsavedEdit = 0
      giveWindowTitle()
      self.ui.dataIndex.xmltree = etree.parse(self.ui.dataIndex.sourceFile)
      self.ui.dataIndex.root = self.ui.dataIndex.xmltree.getroot()
      
    self.ui.actionOpen.triggered.connect(openDb)

    '''Open Recent'''
            
    def openRecentDb(Fieldbook, currentFile, recentItem):
        if currentFile:
            if not okToContinue():
                return
        fname = recentItem
        self.ui.tabWidget.setCurrentIndex(0)
        if fname:
            Fieldbook.ui.dataIndex.xmltree = etree.parse(fname)
            Fieldbook.ui.dataIndex.root = Fieldbook.ui.dataIndex.xmltree.getroot()
            #rebuild the window contents using the new file
            Fieldbook.ui.dataIndex.lexDict.clear()
            Fieldbook.ui.dataIndex.textDict.clear()
            Fieldbook.ui.dataIndex.dataDict.clear()
            Fieldbook.ui.hLexNav.clear()
            Fieldbook.ui.lLexNav.clear()
            Fieldbook.ui.hTextNav.clear()
            Fieldbook.ui.tTextNav.clear()      
            Fieldbook.ui.hDataNav.clear()
            Fieldbook.ui.dDataNav.clear()
            self.ui.tabWidget.setTabEnabled(1,1)
            self.ui.tabWidget.setTabEnabled(2,1)
            self.ui.tabWidget.setTabEnabled(3,1)
            self.ui.tabWidget.setTabEnabled(4,1)
            self.ui.tabWidget.setTabEnabled(5,1)
            self.ui.tabWidget.setTabEnabled(6,1)
            self.ui.tabWidget.setTabEnabled(7,1)
            self.ui.tabWidget.setTabEnabled(8,1)
            navLexEntry()
            navText()
            navDset()
            makeAbbrList()
            fillConsultantTable()
            dbTitle = Fieldbook.ui.dataIndex.root.attrib.get('Dbase')
            Fieldbook.ui.hTitle.setText(dbTitle)
            Fieldbook.ui.hTitle.setAlignment(QtCore.Qt.AlignHCenter)
            lang = Fieldbook.ui.dataIndex.root.attrib.get('Language')
            Fieldbook.ui.hLanguage.setText(lang)
            family = Fieldbook.ui.dataIndex.root.attrib.get('Family')
            Fieldbook.ui.hFamily.setText(family)
            population = Fieldbook.ui.dataIndex.root.attrib.get('Population')
            Fieldbook.ui.hPopulation.setText(population)
            location = Fieldbook.ui.dataIndex.root.attrib.get('Location')
            Fieldbook.ui.hLocation.setText(location)
            iso = Fieldbook.ui.dataIndex.root.attrib.get('ISO')
            Fieldbook.ui.hISO.setText(iso)
            return fname
        else:
            openDb()

    def oRecent1():
      currentFile = self.ui.dataIndex.sourceFile
      recentItem = self.ui.dataIndex.recentFile[0]
      del self.ui.dataIndex.recentFile[0]
      fname = openRecentDb(self, currentFile, recentItem)
      unsavedEdit = 0
      self.ui.dataIndex.recentFile = updateRecentFile(self.ui.dataIndex.recentFile, currentFile)
      self.ui.dataIndex.sourceFile = fname
      giveWindowTitle()

    def oRecent2():
      currentFile = self.ui.dataIndex.sourceFile
      recentItem = self.ui.dataIndex.recentFile[1]
      del self.ui.dataIndex.recentFile[1]
      fname = openRecentDb(self, currentFile, recentItem)
      self.ui.dataIndex.unsavedEdit = 0
      self.ui.dataIndex.recentFile = updateRecentFile(self.ui.dataIndex.recentFile, currentFile)
      self.ui.dataIndex.sourceFile = fname
      giveWindowTitle()
      
    def oRecent3():
      currentFile = self.ui.dataIndex.sourceFile
      recentItem = self.ui.dataIndex.recentFile[2]
      del self.ui.dataIndex.recentFile[2]
      fname = openRecentDb(self, currentFile, recentItem)
      self.ui.dataIndex.unsavedEdit = 0
      self.ui.dataIndex.recentFile = updateRecentFile(self.ui.dataIndex.recentFile, currentFile)
      self.ui.dataIndex.sourceFile = fname
      giveWindowTitle()
    
    def oRecent4():
      currentFile = self.ui.dataIndex.sourceFile
      recentItem = self.ui.dataIndex.recentFile[3]
      del self.ui.dataIndex.recentFile[3]
      fname = openRecentDb(self, currentFile, recentItem)
      self.ui.dataIndex.unsavedEdit = 0
      self.ui.dataIndex.recentFile = updateRecentFile(self.ui.dataIndex.recentFile, currentFile)
      self.ui.dataIndex.sourceFile = fname
      giveWindowTitle()

    def oRecent5():
      currentFile = self.ui.dataIndex.sourceFile
      recentItem = self.ui.dataIndex.recentFile[4]
      del self.ui.dataIndex.recentFile[4]
      fname = openRecentDb(self, currentFile, recentItem)
      self.ui.dataIndex.unsavedEdit = 0
      self.ui.dataIndex.recentFile = updateRecentFile(self.ui.dataIndex.recentFile, currentFile)
      self.ui.dataIndex.sourceFile = fname
      giveWindowTitle()
    
    self.ui.actionRecent1.triggered.connect(oRecent1)
    self.ui.actionRecent2.triggered.connect(oRecent2)
    self.ui.actionRecent3.triggered.connect(oRecent3)
    self.ui.actionRecent4.triggered.connect(oRecent4)
    self.ui.actionRecent5.triggered.connect(oRecent5)

    '''Close'''
    def closeDb():
      if okToContinue():
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.tabWidget.setTabEnabled(1,0)
        self.ui.tabWidget.setTabEnabled(2,0)
        self.ui.tabWidget.setTabEnabled(3,0)
        self.ui.tabWidget.setTabEnabled(4,0)
        self.ui.tabWidget.setTabEnabled(5,0)
        self.ui.tabWidget.setTabEnabled(6,0)
        self.ui.tabWidget.setTabEnabled(7,0)
        self.ui.tabWidget.setTabEnabled(8,0)
        self.ui.dataIndex.lexDict.clear()
        self.ui.dataIndex.textDict.clear()
        self.ui.dataIndex.dataDict.clear()
        self.ui.hTitle.clear()
        self.ui.hLanguage.clear()
        self.ui.hFamily.clear()
        self.ui.hLocation.clear()
        self.ui.hPopulation.clear()
        self.ui.hISO.clear()
        self.ui.hLexNav.clear()
        self.ui.lLexNav.clear()
        self.ui.hTextNav.clear()
        self.ui.tTextNav.clear()      
        self.ui.hDataNav.clear()
        self.ui.dDataNav.clear()
        self.ui.hLexiconLabel.clear()
        self.ui.hTextsLabel.clear()
        self.ui.hDatasetLabel.clear()
      self.ui.dataIndex.recentFile = updateRecentFile(self.ui.dataIndex.recentFile, self.ui.dataIndex.sourceFile)
      self.ui.dataIndex.unsavedEdit = 0
      self.ui.dataIndex.sourceFile = None
      giveWindowTitle()
 
    self.ui.actionClose.triggered.connect(closeDb) 
     
    '''Save'''
    def saveDb():
      if self.ui.dataIndex.sourceFile != None:
          saveDoc = etree.tostring(self.ui.dataIndex.root, "unicode")
          saveFile = open(self.ui.dataIndex.sourceFile, "w", encoding = "UTF-8")
          saveFile.write(saveDoc)
          saveFile.close()
      else:
          saveAsDb()
      self.ui.dataIndex.unsavedEdit = 0
      settings = QtCore.QSettings()
      settings.setValue('LastFile',self.ui.dataIndex.sourceFile)
      settings.setValue('RecentFile',self.ui.dataIndex.recentFile)
     
    self.ui.actionSave.triggered.connect(saveDb)

    '''Save As'''
    def saveAsDb():
      parent = None
      fname=QtGui.QFileDialog.getSaveFileName(parent, "Save As...")
      if fname:
          saveDoc = etree.tostring(self.ui.dataIndex.root, "unicode")
          saveFile = open(fname, "w", encoding = "UTF-8")
          saveFile.write(saveDoc)
          saveFile.close()
          self.ui.dataIndex.unsavedEdit = 0
          self.ui.dataIndex.sourceFile = fname
          settings = QtCore.QSettings()
          settings.setValue('LastFile',self.ui.dataIndex.sourceFile)
          settings.setValue('RecentFile',self.ui.dataIndex.recentFile)
          giveWindowTitle()

    self.ui.actionSaveAs.triggered.connect(saveAsDb)

    '''new card'''

    def clearCard():
        fieldList = self.ui.tabWidget.currentWidget().findChildren(QtGui.QTextEdit)
        for item in fieldList:
            item.clear()
        plainList = self.ui.tabWidget.currentWidget().findChildren(QtGui.QPlainTextEdit)
        for item in plainList:
            item.clear()
        lineList = self.ui.tabWidget.currentWidget().findChildren(QtGui.QLineEdit)
        for item in lineList:
            item.clear()

    def newCard():
        if self.ui.tabWidget.currentIndex() == 1: #lexicon card
            startCard = self.ui.dataIndex.lexDict[self.ui.dataIndex.currentCard]
            newID = idGenerator.generateID('LX',self.ui.dataIndex.lexDict)
            date = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
            newCdWindow = NewLexWindow()
            if newCdWindow.exec_():
                clearCard()
                self.ui.lL1Definition.clear() 
                self.ui.lL2Definition.clear() 
                self.ui.lDerivatives.clear()
                data = newCdWindow.getData()
                '''returns a list [speaker,researcher,entry word, gloss]'''
                newNode = etree.Element('Lex',{"LexID":newID})
                newNode.set('Date',date)
                newNode.set('Updated',date)
                newNode.set('Spkr',data[0])
                newNode.set('Rschr',data[1])
                newOrth = etree.SubElement(newNode,'Orth')
                newOrth.text = data[2]
                '''generate IPA node if Auto checked'''
                if self.ui.lAutoBtn.isChecked() == True:
                    IPA = Orthographies.toIPA(data[2])
                    newIPA = etree.SubElement(newNode,'IPA')
                    newIPA.text = IPA
                    self.ui.lIPA.setText(IPA)
                newDef = etree.SubElement(newNode,'Def',{'Index':'1'})
                newL1 = etree.SubElement(newDef,'L1')
                newL1.text = data[3]
                self.ui.lSource.setPlainText(data[0])
                self.ui.lResearcher.setPlainText(data[1])
                self.ui.lDate.setPlainText(date)
                self.ui.lUpdated.setPlainText(date)
                self.ui.lOrthography.setText(data[2])
                '''if data[2] is homophonous with another entry'''
                homList = self.ui.lLexNav.findItems(data[2],QtCore.Qt.MatchExactly)
                if homList != None:
                    hom = newID
                    for item in homList:
                        hom += ', ' + item.data(32)
                    newNode.set('Hom',hom)
                    for item in homList:
                        self.ui.dataIndex.lexDict[item.data(32)].set('Hom',hom)
                cardLoader.loadDefinitions(newNode)
                self.ui.dataIndex.root.insert(1,newNode)
                self.ui.dataIndex.lexDict[newID] = newNode
                newItem = QtGui.QListWidgetItem(parent, QtGui.QListWidgetItem.UserType)
                newItem.setText(data[2])
                newItem.setData(32,newID)
                self.ui.lLexNav.addItem(newItem)
                newHItem = QtGui.QListWidgetItem(parent, QtGui.QListWidgetItem.UserType)
                newHItem.setText(data[2])
                newHItem.setData(32,newID)
                self.ui.hLexNav.addItem(newHItem)
##                self.ui.sortNavLists(self.ui.lLexNav,self.ui.hLexNav)
                for i in range(0,self.ui.lLexNav.count()):
                    if self.ui.lLexNav.item(i).data(32) == newID:
                        theItem = i
                        break                    
                self.ui.lLexNav.setCurrentRow(theItem)
                self.ui.lLexNav.scrollToItem(self.ui.lLexNav.currentItem(), QtGui.QAbstractItemView.PositionAtCenter)
                self.ui.hLexNav.setCurrentRow(theItem)
                self.ui.hLexNav.scrollToItem(self.ui.lLexNav.currentItem(), QtGui.QAbstractItemView.PositionAtCenter)
                self.ui.dataIndex.currentCard = newID
                self.ui.dataIndex.lastLex = newID
                self.ui.dataIndex.lexDict[newID] = newNode

        if self.ui.tabWidget.currentIndex() == 2: # text card
            print('text card')
            tableList = self.ui.tText.findChildren(textTable)
            for table in tableList:
                table.setParent(None)
            self.ui.lDerivatives.clear()
            newID = idGenerator.generateID('TX',self.ui.dataIndex.textDict)
            print(newID)

        if self.ui.tabWidget.currentIndex() == 3: # example card
            print('example card')
            self.ui.eAnalysis.setParent(None)
            self.ui.lDerivatives.clear()
            newID = idGenerator.generateID('EX',self.ui.dataIndex.exDict)
            print(newID)

        if self.ui.tabWidget.currentIndex() == 4: # dataset card
            print('dataset card')
            self.ui.lDerivatives.clear()
            newID = idGenerator.generateID('DS',self.ui.dataIndex.dataDict)
            print(newID)

    self.ui.actionNewCard.triggered.connect(newCard)

    def delCard():
        target = self.ui.dataIndex.currentCard
        if self.ui.tabWidget.currentIndex() == 1:
            cardType = "lexical entry"
            badNode = self.ui.dataIndex.lexDict[target]
        if self.ui.tabWidget.currentIndex() == 2:
            cardType = "text"
            badNode = self.ui.dataIndex.textDict[target]
        if self.ui.tabWidget.currentIndex() == 3:
            cardType = "example"
            badNode = self.ui.dataIndex.exDict[target]
        if self.ui.tabWidget.currentIndex() == 4:
            cardType = "dataset"
            badNode = self.ui.dataIndex.dataDict[target]
        if cardType == "example" and badNode.attrib.get('SourceText') != None:
            textTitle = "<i>" + self.ui.eSourceText.toPlainText() + "</i>"
            msgbox = QtGui.QMessageBox()
            msgbox.setIcon(QtGui.QMessageBox.Critical)
            msgbox.setText("Line from text.")
            msgbox.setInformativeText('This is a line from the text %s. Please edit texts from the <b>Texts</b> tab.' %textTitle)
            msgbox.setStandardButtons(QtGui.QMessageBox.Ok)
            msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
            reply = msgbox.exec_()
            return
        else:
            msgbox = QtGui.QMessageBox()
            msgbox.setIcon(QtGui.QMessageBox.Warning)
            msgbox.setText("Delete card?")
            msgbox.setInformativeText("This will remove the current %s and all cross-references to it from the database." %cardType)
            msgbox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
            reply = msgbox.exec_()
            if reply == QtGui.QMessageBox.Ok:
                if cardType == "lexical entry":
                    if self.ui.dataIndex.lexDict[target].attrib.get('Hom') != None:
                        homs = self.ui.dataIndex.lexDict[target].attrib.get('Hom')
                        homList = homs.split(', ')
                        if len(homList) == 2:
                            for item in homList:
                                node = self.ui.dataIndex.lexDict[item]
                                del node.attrib['Hom']
                                print(etree.tostring(node,encoding = 'unicode'))
                        else:
                            homList.remove(target)
                            for i, item in enumerate(homList):
                                if i == 0:
                                    newHom = item
                                else:
                                    newHom += ', ' + item
                            for item in homList:
                                self.ui.dataIndex.lexDict[item].set('Hom',newHom)
                    del self.ui.dataIndex.lexDict[target]
                    for i in range(self.ui.lLexNav.model().rowCount()):
                        if self.ui.lLexNav.model().index(i,0).data(32) == target:
                            self.ui.lLexNav.model().removeRow(i)
                            break
                    print('purge')
                    btnCmds.goPrevLx()
                elif cardType == "text":
                    del self.ui.dataIndex.textDict[target]
                    for i in range(self.ui.tTextNav.model().rowCount()):
                        if self.ui.tTextNav.model().index(i,0).data(32) == target:
                            self.ui.tTextNav.model().removeRow(i)
                            break
                    print('purge')
                    ##remove examples from db
                    msgbox = QtGui.QMessageBox()
                    msgbox.setIcon(QtGui.QMessageBox.Question)
                    msgbox.setText("Remove examples?")
                    msgbox.setInformativeText("Remove all the lines in this text from the database as well?")
                    msgbox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    msgbox.setDefaultButton(QtGui.QMessageBox.Yes)
                    reply = msgbox.exec_()
                    btnCmds.goPrevTxt()
                elif cardType == "example":
                    del self.ui.dataIndex.exDict[target]
                    print('purge')
                    btnCmds.goPrevEg()
                elif cardType == "dataset":
                    del self.ui.dataIndex.dataDict[target]
                    for i in range(self.ui.dDataNav.model().rowCount()):
                        if self.ui.dDataNav.model().index(i,0).data(32) == target:
                            self.ui.dDataNav.model().removeRow(i)
                            break
                    print('purge')
                    btnCmds.goPrevDset()
                self.ui.dataIndex.root.remove(badNode)
                if target in cardStack.theQueue:
                    newList = []
                    for item in cardStack.theQueue:
                        if item != target:
                            newList.append(item)
                        else:
                            cardStack.theCounter -= 1
                    cardStack.theQueue = newList
            else:
                event.ignore()
                return
            self.ui.dataIndex.unsavedEdit = 1

    self.ui.actionDelCard.triggered.connect(delCard)

        
    ### end menu actions definitions ##

    '''Set default menubar (= Home tab menubar)'''
    
    leaveTab()

## def __init ends here ##
    
  def closeEvent(self, event):
     if self.ui.dataIndex.sourceFile != None and self.ui.dataIndex.unsavedEdit == 1:
       msgbox = QtGui.QMessageBox()
       msgbox.setText("Any unsaved changes will be lost.")
       msgbox.setInformativeText("Do you want to save changes?")
       msgbox.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
       msgbox.setDefaultButton(QtGui.QMessageBox.Save)
       reply = msgbox.exec_()
       if reply == QtGui.QMessageBox.Cancel:
         event.ignore()
         return
       elif reply == QtGui.QMessageBox.Save:
         QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
         self.ui.dataIndex.xmltree.write(self.ui.dataIndex.sourceFile, encoding="UTF-8")
         QtGui.QApplication.restoreOverrideCursor()
     settings = QtCore.QSettings()
     settings.setValue('LastFile',self.ui.dataIndex.sourceFile)
     settings.setValue('RecentFile',self.ui.dataIndex.recentFile)

class HTMLDelegate(QtGui.QStyledItemDelegate):
        
    def paint(self, painter, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options,index)

        style = QtGui.QApplication.style() if options.widget is None else options.widget.style()
##        tOption = QtGui.QTextOption()
##        tOption.setWrapMode(QtGui.QTextOption.WordWrap)

        doc = QtGui.QTextDocument()
##        doc.setDefaultTextOption(tOption)
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter);

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QtGui.QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options,index)
##        tOption = QtGui.QTextOption()
##        tOption.setWrapMode(QtGui.QTextOption.WordWrap)

        doc = QtGui.QTextDocument()
##        doc.setDefaultTextOption(tOption)
        doc.setHtml(options.text)
        return QtCore.QSize(doc.idealWidth(), doc.size().height())

class textTable(QtGui.QTableWidget):
    '''class defines the properties of the text field on the text card'''

    class selectionData:
        openCell = None
        openCellText = ''
        lineNumber = ''
      
    def __init__(self, parent):
        super(textTable, self).__init__(parent)
        self.itemClicked.connect(self.cellClicked)
        self.itemSelectionChanged.connect(self.updateExample)
        self.SelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setStyleSheet("selection-background-color: #E6E6E6;")
        delegate = HTMLDelegate()
        self.setItemDelegate(delegate)
        self.horizontalHeader().setEnabled(0)
        self.verticalHeader().setEnabled(0)
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.setShowGrid(0)
        self.setMinimumHeight(95)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.MinimumExpanding)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                          
    def formatHandler(theString):
        if "<" in theString:
            theString = theString.replace("<","{{")
            theString = theString.replace(">","}}")
        return theString

    def updateExample(self):
        if self.selectionData.openCell != None:
            if self.selectionData.openCellText != self.selectionData.openCell.text():
                myapp.ui.dataIndex.unsavedEdit = 1
                update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
                myapp.ui.lUpdated.setPlainText(update)
                ExNode = self.item(0,0).data(35)
                ExNode.set('Update',update)
                mrph = ''
                ileg = ''
                gloss = self.item(3,1).text()
                line = self.item(0,1).text()
                for i in range(1,self.columnCount()):
                    if self.columnCount() == 2:
                        self.resizeColumnToContents(1)
                    elif i == 1:
                        lineItem = self.takeItem(0,1)
                        glossItem = self.takeItem(3,1)
                        lastItem = self.takeItem(2,self.columnCount()-1)
                        self.setItem(2,self.columnCount()-1,glossItem)
                        self.resizeColumnToContents(self.columnCount()-1)
                        self.takeItem(2,self.columnCount()-1)
                        self.setItem(0,1,lineItem)
                        self.setItem(3,1,glossItem)
                        self.setItem(2,self.columnCount()-1,lastItem)
                        self.setSpan(0,1,1,self.columnCount()-1)
                        self.setSpan(3,1,1,self.columnCount()-1)
                    elif i == self.columnCount()-1:
                        pass
                    else:
                        self.resizeColumnToContents(i)
                    mrphItem = self.item(1,i).text()
                    ilegItem = self.item(2,i).text()
                    if i > 1:
                        mrph = mrph + '\t' + mrphItem
                        ileg = ileg + '\t' + ilegItem
                    else:
                        mrph = mrphItem
                        ileg = ilegItem
                ExNode.find('Mrph').text = mrph
                ExNode.find('ILEG').text = textTable.formatHandler(ileg)
                ExNode.find('Line').text = textTable.formatHandler(line)
                ExNode.find('L1Gloss').text = textTable.formatHandler(gloss)
                ##needs to handle L2 option

    def cellClicked(self,item):
        if self.selectionData.openCell != None:
            try:
                self.selectionData.openCell.setSelected(0)
            except RuntimeError:
                pass
        if self.currentColumn() == 0:
            ExNode = self.item(0,0).data(35)
            cardLoader.loadEgCard(myapp,ExNode)
            myapp.ui.tabWidget.setCurrentIndex(3)
        else:
            self.selectionData.openCell = item
            self.selectionData.openCellText = item.text()
            myapp.ui.dataIndex.lineNumber = self.item(0,0).text()
            myapp.ui.tNewLineBtn.setEnabled(1)
            myapp.ui.tRemoveLineBtn.setEnabled(1)
            myapp.ui.tSplitLineBtn.setEnabled(1)
            myapp.ui.tAnalyzeBtn.setEnabled(1)
            myapp.ui.dataIndex.currentTextTable = item.tableWidget()
            self.editItem(item)
            
class EgTable(QtGui.QTableWidget):
    '''class defines the properties of the example field on the example card'''

    class selectionData:
        openCell = None
        openCellText = ''
        openColumn = -1
      
    def __init__(self, parent):
        super(EgTable, self).__init__(parent)
        self.itemDoubleClicked.connect(self.cellClicked)
        self.itemSelectionChanged.connect(self.updateTable)
        self.SelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setStyleSheet("selection-background-color: #E6E6E6")
        delegate = HTMLDelegate()
        self.setItemDelegate(delegate)
        self.horizontalHeader().setEnabled(1)
        self.verticalHeader().setEnabled(0)
        self.verticalHeader().hide()
        self.horizontalHeader().show()
        self.horizontalHeader().sectionClicked.connect(self.headerClicked)
        self.setShowGrid(0)
        self.setMinimumHeight(95)
        self.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.MinimumExpanding)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                          
    def formatHandler(theString):
        if "<" in theString:
            theString = theString.replace("<","{{")
            theString = theString.replace(">","}}")
        return theString

    def headerClicked(self):
        colLoc = self.columnCount()-1
        if colLoc ==  self.currentColumn():
            self.insertColumn(colLoc)
        for i in range(0,self.rowCount()):
            newItem = QtGui.QTableWidgetItem(1001)
            self.setItem(i,colLoc,newItem)
            self.updateExample()

    def updateTable(self):
        if self.currentColumn() + 1 != self.columnCount():
            '''if the selected cell is in the table but not the last column in the table'''
            self.updateExample()
            return

    def updateExample(self):
        if self.selectionData.openCell != None:
            if self.selectionData.openCellText != self.selectionData.openCell.text():
                myapp.ui.dataIndex.unsavedEdit = 1
                update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
                myapp.ui.lUpdated.setPlainText(update)
                for child in myapp.ui.dataIndex.root.iter('Ex'):
                    if child.attrib.get('ExID') == myapp.ui.dataIndex.currentCard:
                        ExNode = child
                ExNode.set('Update',update)
                mrph = ''
                ileg = ''
                for i in range(0,self.columnCount()-1):
                    try:
                        mrphItem = self.item(0,i).text()
                        ilegItem = self.item(1,i).text()
                    except AttributeError:
                        break                           
                    if i > 0:
                        mrph = mrph + '\t' + mrphItem
                        ileg = ileg + '\t' + ilegItem
                    else:
                        mrph = mrphItem
                        ileg = ilegItem
                ExNode.find('Mrph').text = mrph
                ExNode.find('ILEG').text = EgTable.formatHandler(ileg)
                ##needs to handle L2 option
            if self.selectionData.openColumn != -1:
                self.resizeColumnToContents(self.selectionData.openColumn)
            else:
                self.resizeColumnToContents(self.currentColumn())

    def cellClicked(self,item):
        self.selectionData.openCell = item
        self.selectionData.openCellText = item.text()
        self.selectionData.openColumn = self.currentColumn()
        myapp.ui.dataIndex.currentTextTable = item.tableWidget()
        self.editItem(item)
##        myapp.ui.tNewLineBtn.setEnabled(1)
##        myapp.ui.tRemoveLineBtn.setEnabled(1)
##        myapp.ui.tSplitLineBtn.setEnabled(1)
##        myapp.ui.tAnalyzeBtn.setEnabled(1)
##        self.openPersistentEditor(item)

class DefTable(QtGui.QTableWidget):
    '''class defines the properties of the definition fields on the lexicon card'''
    def __init__(self):
        super(DefTable, self).__init__()
        self.initUI()
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("selection-background-color: #F0F0F0;")
        delegate = HTMLDelegate()
        self.setItemDelegate(delegate)
        self.itemClicked.connect(self.cellClicked)
            
    def initUI(self):
        self.setGeometry(QtCore.QRect(9, 28, 681, 112))
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setShowGrid(0)
                
    def cellClicked(self,item):
        if item.data(35) != None:
            exRoot = myapp.ui.dataIndex.exDict[item.data(35)]
            cardLoader.loadEgCard(myapp,exRoot)
            myapp.ui.tabWidget.setCurrentIndex(3)
        else:
            global fManager
            fManager = FieldManager()
            fManager.exec()
            
class GrmField(QtGui.QTextEdit):
    '''class defines the properties of the grammar field on the lexicon card'''
    def __init__(self):
        super(GrmField, self).__init__()
        self.initUI()

    def initUI(self):
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setReadOnly(True)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.setObjectName("lGrammar")

    def mouseDoubleClickEvent(* event):
        global gManager
        gManager = GrammarManager()
        gManager.setValues(myapp.ui.dataIndex.currentCard)
        gManager.exec()

class NewLexWindow(QtGui.QDialog):

    class tabFilter(QtCore.QObject):
        def __init__(self, parent=None):
            super(NewLexWindow.tabFilter, self).__init__(parent)

        def eventFilter(self, object, event):
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Tab:
                    object.parent().focusNextChild()
                elif event.key() == QtCore.Qt.Key_Backtab:
                    object.parent().focusPreviousChild()
                else:
                    return self.event(event)
                return True
                
            return self.event(event)

    class windowData():
        prevEdit = 0
        
    def __init__(self, parent=None):
        super(NewLexWindow,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.setObjectName(_fromUtf8("NewLexWindow"))
        self.resize(380, 305)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)
        self.explanation = QtGui.QLabel(self)
        self.explanation.setGeometry(QtCore.QRect(12, 10, 360, 35))
        self.explanation.setObjectName(_fromUtf8("explanation"))
        
        self.metaBox = QtGui.QGroupBox(self)
        self.metaBox.setGeometry(QtCore.QRect(10, 55, 360, 85))
        self.metaBox.setObjectName(_fromUtf8("metaBox"))
        self.mLayout = QtGui.QHBoxLayout(self.metaBox)
        self.sLayout = QtGui.QVBoxLayout()
        self.speakerLabel = QtGui.QLabel(parent=None)
        self.speakerLabel.setObjectName(_fromUtf8("SpkrLabel"))
        self.speakerCode = QtGui.QComboBox()
        self.speakerCode.setObjectName(_fromUtf8("SpeakerCode"))
        self.speakerCode.setFixedHeight(30)
        self.speakerCode.setFixedWidth(240)
        self.speakerCode.activated.connect(self.setSpeaker)
        self.sLayout.addWidget(self.speakerLabel,0)
        self.sLayout.addWidget(self.speakerCode,1)
        self.mLayout.addLayout(self.sLayout)

        self.rLayout = QtGui.QVBoxLayout()
        self.rschrLabel = QtGui.QLabel(parent=None)
        self.rschrLabel.setObjectName(_fromUtf8("RschrLabel"))
        self.researcherCode = QtGui.QComboBox()
        self.researcherCode.setObjectName(_fromUtf8("ResearcherCode"))
        self.researcherCode.setFixedHeight(30)
        self.researcherCode.setFixedWidth(70)
        self.researcherCode.activated.connect(self.setRschr)
        self.rLayout.addWidget(self.rschrLabel,0)
        self.rLayout.addWidget(self.researcherCode,1)
        self.mLayout.addLayout(self.rLayout)
        self.metaBox.setLayout(self.mLayout)

        self.elemBox = QtGui.QGroupBox(self)
        self.elemBox.setGeometry(QtCore.QRect(10, 150, 360, 100))
        self.elemBox.setObjectName(_fromUtf8("elemBox"))
        self.entryWord = QtGui.QTextEdit()
        self.filter = NewLexWindow.tabFilter()
        self.entryWord.installEventFilter(self.filter)
        self.gloss = QtGui.QTextEdit()
        self.gloss.installEventFilter(self.filter)
        fLayout = QtGui.QFormLayout(self.elemBox)
        fLayout.addRow("Entry word",self.entryWord)
        fLayout.addRow("Gloss",self.gloss)
        self.elemBox.setLayout(fLayout)

        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 255, 360, 56))
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        self.ButtonBox.setFlat(True)
        self.bLayout = QtGui.QHBoxLayout(self.ButtonBox)
        self.CancelBtn = QtGui.QPushButton(self.ButtonBox)
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)
        spacerItem = QtGui.QSpacerItem(141, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.bLayout.addItem(spacerItem)
        self.bLayout.addWidget(self.CancelBtn)
        self.AddBtn = QtGui.QPushButton(self.ButtonBox)
        self.AddBtn.setObjectName(_fromUtf8("AddBtn"))
        self.AddBtn.clicked.connect(self.OK)       
        self.bLayout.addWidget(self.AddBtn)
        self.AddBtn.setDefault(1)
            
        codeList = sorted(myapp.ui.dataIndex.speakerDict.keys())
        for index, item in enumerate(codeList):
            fullName = myapp.ui.dataIndex.speakerDict.get(item).findtext('Name')
            item += ' (' + fullName + ')'
            codeList[index] = item
        self.speakerCode.insertItems(0,codeList)
        if myapp.ui.dataIndex.lastSpeaker:
            j = self.speakerCode.findText(myapp.ui.dataIndex.lastSpeaker,QtCore.Qt.MatchStartsWith)
            self.speakerCode.setCurrentIndex(j)        
        
        codeList = sorted(myapp.ui.dataIndex.rschrDict.keys())
        self.researcherCode.insertItems(0,codeList)                                
        if myapp.ui.dataIndex.lastRschr:
            j = self.researcherCode.findText(myapp.ui.dataIndex.lastRschr,QtCore.Qt.MatchExactly)
            self.researcherCode.setCurrentIndex(j)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        if myapp.ui.dataIndex.unsavedEdit == 1:
            self.windowData.prevEdit = 1

        self.entryWord.setFocus()

    def tabKey(self):
        print('tab')

    def setSpeaker(self):
        lastSpeaker = self.speakerCode.currentText().split(None,1)
        myapp.ui.dataIndex.lastSpeaker = lastSpeaker[0]
        myapp.ui.dataIndex.unsavedEdit = 1

    def setRschr(self):
        lastRschr = self.researcherCode.currentText().split(None,1)
        myapp.ui.dataIndex.lastRschr = lastRschr[0]
        myapp.ui.dataIndex.unsavedEdit = 1

    def getData(self):
        metaData = []
        speaker = self.speakerCode.currentText().split(None,1)
        metaData.append(speaker[0])
        metaData.append(self.researcherCode.currentText())
        metaData.append(self.entryWord.toPlainText())
        metaData.append(self.gloss.toPlainText())
        return metaData

    def cancelled(self,checked):
        if self.windowData.prevEdit == 0:
            myapp.ui.dataIndex.unsavedEdit = 0
        self.reject()

    def OK(self,checked):
        if len(self.entryWord.toPlainText()) == 0 or len(self.gloss.toPlainText()) == 0:
            self.badBox = QtGui.QMessageBox()
            self.badBox.setIcon(QtGui.QMessageBox.Warning)
            self.badBox.setStandardButtons(QtGui.QMessageBox.Ok)
            self.badBox.setDefaultButton(QtGui.QMessageBox.Ok)
            self.badBox.setText('Incomplete entry.')
            self.badBox.setInformativeText('Provide a form and a gloss '
                                           'in the primary working language.')
            self.badBox.exec_()
            return
        myapp.ui.dataIndex.unsavedEdit = 1
        self.accept()

    def retranslateUi(self, NewLexWindow):
        NewLexWindow.setWindowTitle(QtGui.QApplication.translate("NewLexWindow", "New lexical entry", None, QtGui.QApplication.UnicodeUTF8))
        self.AddBtn.setText(QtGui.QApplication.translate("NewLexWindow", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.AddBtn.setToolTip(QtGui.QApplication.translate("NewLexWindow", "add new entry", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("NewLexWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setToolTip(QtGui.QApplication.translate("NewLexWindow", "exit without adding", None, QtGui.QApplication.UnicodeUTF8))
        self.entryWord.setToolTip(QtGui.QApplication.translate("NewLexWindow", "orthographic form of entry", None, QtGui.QApplication.UnicodeUTF8))
        self.gloss.setToolTip(QtGui.QApplication.translate("NewLexWindow", "gloss in primary working language", None, QtGui.QApplication.UnicodeUTF8))
        self.explanation.setText(QtGui.QApplication.translate("NewLexWindow", "Provide the information required to start a new entry.\n"
                                                              "Additional information can be added in the tab view.", None, QtGui.QApplication.UnicodeUTF8))
        self.rschrLabel.setText(QtGui.QApplication.translate("NewLexWindow", "Researcher", None, QtGui.QApplication.UnicodeUTF8))
        self.speakerLabel.setText(QtGui.QApplication.translate("NewLexWindow", "Speaker", None, QtGui.QApplication.UnicodeUTF8))

class FieldManager(QtGui.QDialog):
    '''class for constraining user input to lexicon def fields'''

    class editState():
        unsavedEdit = 0

    class focusOutFilter(QtCore.QObject):
      def __init__(self, parent=None):
        super(FieldManager.focusOutFilter, self).__init__(parent)
      
      def eventFilter(self, object, event):
          if event.type() == QtCore.QEvent.FocusOut:
            try:
                object.clearSelection()
            except AttributeError:
                pass
          return False
            
    class paletteField(QtGui.QTextEdit):
        def __init__(self, parent):
            super(FieldManager.paletteField, self).__init__(parent)
            self.filter = FieldManager.focusOutFilter()
            self.installEventFilter(self.filter)
            self.textChanged.connect(self.flagUnsavedEdits)

        def flagUnsavedEdits(self):
          FieldManager.editState.unsavedEdit = 1
          if len(fManager.L1.toPlainText()) != 0:
              fManager.Update.setDisabled(0)
          
    class L1Field(paletteField):
        def __init__(self, parent):
            super(FieldManager.L1Field, self).__init__(parent)
            self.textChanged.connect(FieldManager.activateAddButton)
        
    class lexTable(QtGui.QTableWidget):
        def __init__(self, parent):
            super(FieldManager.lexTable, self).__init__(parent)
            self.setStyleSheet("selection-background-color: #F0F0F0;")
            delegate = HTMLDelegate()
            self.setItemDelegate(delegate)
            self.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)

    class exTable(lexTable):
        def __init__(self, parent):
            super(FieldManager.exTable, self).__init__(parent)
            self.cellClicked.connect(FieldManager.activateMinusEg)
            self.cellDoubleClicked.connect(self.findEg)

        def findEg(self, row, column):
            print(self.item(row,column).data(36))
                
    def __init__(self, parent=None):
        super(FieldManager,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        class FmData:
            currentCell = []
            currentSubentry = 0
        
        self.FmData = FmData()
        self.setObjectName(_fromUtf8("FieldManager"))
        self.resize(531, 767)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)
        self.lexBox = QtGui.QGroupBox(self)
        self.lexBox.setGeometry(QtCore.QRect(10, 9, 511, 238))
        self.lexBox.setObjectName(_fromUtf8("lexBox"))
        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 708, 511, 56))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonBox.sizePolicy().hasHeightForWidth())
        self.ButtonBox.setSizePolicy(sizePolicy)
        self.ButtonBox.setTitle(_fromUtf8(""))
        self.ButtonBox.setFlat(True)
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ButtonBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.orderEntries = QtGui.QSpinBox(self.ButtonBox)
        self.orderEntries.setObjectName(_fromUtf8("orderEntries"))
        self.orderEntries.setDisabled(1)
        self.orderEntries.setMaximum(0)
        self.orderEntries.valueChanged.connect(self.reorderEntries)
        self.horizontalLayout.addWidget(self.orderEntries)
        spacerItem = QtGui.QSpacerItem(141, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.Clear = QtGui.QPushButton(self.ButtonBox)
        self.Clear.setObjectName(_fromUtf8("Clear"))
        self.Clear.clicked.connect(self.clearAll)
        self.Clear.setDisabled(1)
        self.horizontalLayout.addWidget(self.Clear)
        self.Kill = QtGui.QPushButton(self.ButtonBox)
        self.Kill.setObjectName(_fromUtf8("Kill"))
        self.Kill.clicked.connect(self.killSubentry)
        self.Kill.setDisabled(1)
        self.horizontalLayout.addWidget(self.Kill)
        self.New = QtGui.QPushButton(self.ButtonBox)
        self.New.setObjectName(_fromUtf8("New"))
        self.New.clicked.connect(self.newSubEntry)
        self.New.setDisabled(1)
        self.horizontalLayout.addWidget(self.New)
        self.Update = QtGui.QPushButton(self.ButtonBox)
        self.Update.setObjectName(_fromUtf8("Update"))
        self.Update.clicked.connect(self.updateXML)
        self.horizontalLayout.addWidget(self.Update)
        self.Update.setDisabled(1)
        self.CancelBtn = QtGui.QPushButton(self.ButtonBox)
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)       
        self.horizontalLayout.addWidget(self.CancelBtn)
        self.OkayBtn = QtGui.QPushButton(self.ButtonBox)
        self.OkayBtn.setObjectName(_fromUtf8("OkayBtn"))
        self.OkayBtn.setDefault(1)
        self.horizontalLayout.addWidget(self.OkayBtn)
        self.OkayBtn.clicked.connect(self.OK)
        
        self.fieldBox = QtGui.QGroupBox(self)
        self.fieldBox.setGeometry(QtCore.QRect(10, 254, 510, 448))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fieldBox.sizePolicy().hasHeightForWidth())
        self.fieldBox.setSizePolicy(sizePolicy)
        self.fieldBox.setAutoFillBackground(True)
        self.fieldBox.setTitle(_fromUtf8(""))
        self.fieldBox.setObjectName(_fromUtf8("fieldBox"))
        self.addEgBtn = QtGui.QPushButton(self.fieldBox)
        self.addEgBtn.setGeometry(QtCore.QRect(15, 344, 20, 20))
        self.addEgBtn.setObjectName(_fromUtf8("addEgBtn"))
        self.addEgBtn.clicked.connect(self.addEg)
        self.minusEgBtn = QtGui.QPushButton(self.fieldBox)
        self.minusEgBtn.setGeometry(QtCore.QRect(45, 344, 20, 20))
        self.minusEgBtn.setObjectName(_fromUtf8("minusEgBtn"))
        self.minusEgBtn.clicked.connect(self.minusEg)
        self.minusEgBtn.setDisabled(1)
        self.switchEgBtn = QtGui.QPushButton(self.fieldBox)
        self.switchEgBtn.setGeometry(QtCore.QRect(4, 368, 72, 32))
        self.switchEgBtn.setObjectName(_fromUtf8("switchEgBtn"))
        self.switchEgBtn.clicked.connect(self.switchEg)
        self.switchEgBtn.setDisabled(1)

        self.diaBox = QtGui.QGroupBox(self.fieldBox)
        self.diaBox.setGeometry(10, 10, 490, 90)
        self.Part = QtGui.QLabel(self.diaBox)
        self.Part.setGeometry(QtCore.QRect(10, 8, 50, 16))
        self.Part.setObjectName(_fromUtf8("Part"))
        self.Speech = QtGui.QLabel(self.diaBox)
        self.Speech.setGeometry(QtCore.QRect(10, 22, 62, 16))
        self.Speech.setObjectName(_fromUtf8("Speech"))
        self.POS = self.paletteField(self.diaBox)
        self.POS.setGeometry(QtCore.QRect(80, 10, 144, 25))
        self.POS.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.POS.setObjectName(_fromUtf8("POS"))
        self.Register = QtGui.QLabel(self.diaBox)
        self.Register.setGeometry(QtCore.QRect(260, 14, 52, 16))
        self.Register.setObjectName(_fromUtf8("Register"))
        self.Reg = self.paletteField(self.diaBox)
        self.Reg.setGeometry(QtCore.QRect(338, 10, 144, 25))
        self.Reg.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Reg.setObjectName(_fromUtf8("Reg"))
        self.Dialect = QtGui.QLabel(self.diaBox)
        self.Dialect.setGeometry(QtCore.QRect(10, 52, 44, 16))
        self.Dialect.setObjectName(_fromUtf8("Dialect"))
        self.Dia = self.paletteField(self.diaBox)
        self.Dia.setGeometry(QtCore.QRect(80, 48, 144, 25))
        self.Dia.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Dia.setObjectName(_fromUtf8("Dia"))
        self.AltLabel = QtGui.QLabel(self.diaBox)
        self.AltLabel.setGeometry(QtCore.QRect(260, 52, 80, 16))
        self.AltLabel.setObjectName(_fromUtf8("Alternate"))
        self.Alternative = self.paletteField(self.diaBox)
        self.Alternative.setGeometry(QtCore.QRect(338, 48, 144, 25))
        self.Alternative.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.Alternative.setObjectName(_fromUtf8("Alternative"))

        self.PLanguage = QtGui.QLabel(self.fieldBox)
        self.PLanguage.setGeometry(QtCore.QRect(10, 148, 62, 16))
        self.PLanguage.setObjectName(_fromUtf8("PLanguage"))
        self.SLanguage = QtGui.QLabel(self.fieldBox)
        self.SLanguage.setGeometry(QtCore.QRect(10, 226, 62, 16))
        self.SLanguage.setObjectName(_fromUtf8("SLanguage"))
        self.Primary = QtGui.QLabel(self.fieldBox)
        self.Primary.setGeometry(QtCore.QRect(10, 129, 59, 24))
        self.Primary.setObjectName(_fromUtf8("Primary"))
        self.L1 = self.L1Field(self.fieldBox)
        self.L1.setGeometry(QtCore.QRect(90, 115, 410, 70))
        self.L1.setObjectName(_fromUtf8("L1"))
        self.Secondary = QtGui.QLabel(self.fieldBox)
        self.Secondary.setGeometry(QtCore.QRect(10, 208, 72, 20))
        self.Secondary.setObjectName(_fromUtf8("Secondary"))
        self.L2 = self.paletteField(self.fieldBox)
        self.L2.setGeometry(QtCore.QRect(90, 195, 410, 70))
        self.L2.setObjectName(_fromUtf8("L2"))
        self.Examples = QtGui.QLabel(self.fieldBox)
        self.Examples.setGeometry(QtCore.QRect(10, 322, 62, 16))
        self.Examples.setObjectName(_fromUtf8("Examples"))
        self.LnBox = QtGui.QGroupBox(self.fieldBox)
        self.LnBox.setGeometry(QtCore.QRect(90, 295, 410, 140))
        self.LnBox.setObjectName(_fromUtf8("LnBox"))
        self.Ln = self.exTable(self.LnBox)
        self.Ln.setGeometry(QtCore.QRect(2, 2, 406, 136))
        self.Ln.setRowCount(0)
        self.Ln.horizontalHeader().setEnabled(0)
        self.Ln.horizontalHeader().hide()
        self.Ln.verticalHeader().setEnabled(0)
        self.Ln.verticalHeader().hide()
        self.Ln.setColumnCount(1)
        self.Ln.setColumnWidth(0,406)
        self.Ln.setSortingEnabled(0)
        self.Ln.setObjectName(_fromUtf8("Ln"))
        self.table = self.lexTable(self.lexBox)
        self.table.setGeometry(0,0,510,236)
        self.table.setRowCount(1)
        self.table.horizontalHeader().setEnabled(0)
        self.table.horizontalHeader().hide()
        self.table.setColumnCount(1)
        self.table.setColumnWidth(0,510)
        self.table.setSortingEnabled(0)
        self.table.setObjectName(_fromUtf8("subTable"))               
        self.table.cellClicked.connect(self.fillForm)
        address = myapp.ui.dataIndex.currentCard
        for child in myapp.ui.dataIndex.root.iter('Lex'):
            if child.attrib.get('LexID') == address: #locates entry node
                self.FmData.child = child
                break
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.fillTable()
          
    def reorderEntries(self,newValue):
        '''reorders subentries when spin box is clicked'''
        if newValue == 0 or self.FmData.currentSubentry == 0:
            return
        if newValue == self.FmData.currentSubentry:
            return
        ##rearrange XML and renumber Index attrib
        numberDefs = self.table.rowCount()
        child = self.FmData.child
        elemList = list(child)
        for i in range(2,len(elemList)):
            if elemList[i].tag == 'Def':
                firstDef = i
                break
        insertPoint = firstDef + newValue - 1
        def2move = firstDef + self.FmData.currentSubentry - 1
        a = child[def2move]
        child.remove(child[def2move])
        child.insert(insertPoint,a)
        if newValue < self.FmData.currentSubentry:
            self.FmData.currentSubentry -= 1
        elif newValue > self.FmData.currentSubentry:
            self.FmData.currentSubentry += 1

        index = 0
        for Def in child.iter('Def'):
            index += 1
            Def.set('Index',str(index))
            
        self.table.setCurrentCell(self.FmData.currentSubentry-1,0)
        self.editState.unsavedEdit = 1
       
        ##fix display (self.table)
        self.fillTable()

    def switchEg(self):
        '''moves examples to another subentry'''
        self.switchEgDialog = QtGui.QInputDialog()
        self.switchEgDialog.setLabelText('Which subentry would you like<br />to move the example to?')
        result = self.switchEgDialog.exec_()
        if result == 1:
            moveTarget = self.switchEgDialog.textValue()
            try:
                eNumber = int(moveTarget)
            except ValueError:
                self.badBox = QtGui.QMessageBox()
                self.badBox.setIcon(QtGui.QMessageBox.Warning)
                self.badBox.setStandardButtons(QtGui.QMessageBox.Cancel)
                self.badBox.setStandardButtons(QtGui.QMessageBox.Ok)
                self.badBox.setDefaultButton(QtGui.QMessageBox.Ok)
                self.badBox.setText('Index error.')
                self.badBox.setInformativeText('Enter the number of one of<br />'
                                               'the subentries for this word.')
                self.badBox.exec_()
                return
            if eNumber > self.table.rowCount() or eNumber <= 0:
                self.badBox = QtGui.QMessageBox()
                self.badBox.setIcon(QtGui.QMessageBox.Warning)
                self.badBox.setStandardButtons(QtGui.QMessageBox.Cancel)
                self.badBox.setStandardButtons(QtGui.QMessageBox.Ok)
                self.badBox.setDefaultButton(QtGui.QMessageBox.Ok)
                self.badBox.setText('Index out of range error.')
                self.badBox.setInformativeText('Enter the number of one of<br />'
                                               'the existing subentries.')
                self.badBox.exec_()
                return
            if eNumber == self.orderEntries.value():
                return
        else:
            return

        ##change the XML
        currentLoc = self.orderEntries.value() - 1
        ex2Move = self.Ln.currentRow()
        child = self.FmData.child
        elemList = list(child)
        for i in range(2,len(elemList)):
            if elemList[i].tag == 'Def':
                pointer = i
                break
        currentLoc += pointer
        elemList = list(child[currentLoc])
        for i in range(2,len(elemList)):
            if elemList[i].tag == 'Ln':
                pointer2 = i
                break
        ex2Move += pointer2
        transplant = etree.tostring(child[currentLoc][ex2Move],encoding='unicode')
        newEg = etree.XML(transplant)
        child[currentLoc].remove(child[currentLoc][ex2Move])
        newLoc = pointer + eNumber - 1
        elemList = list(child[newLoc])
        insertPoint = len(elemList)
        child[newLoc].insert(insertPoint,newEg)
       
        ##update eg table
        thisRow = self.Ln.currentRow()
        self.Ln.removeRow(thisRow)
        self.minusEgBtn.setDisabled(1)
        self.switchEgBtn.setDisabled(1)

        self.editState.unsavedEdit = 1
            
    def activateMinusEg():
        '''enables the remove example and the switch example buttons'''
        fManager.minusEgBtn.setDisabled(0)
        fManager.switchEgBtn.setDisabled(0)

    def activateAddButton():
        '''enables the add new subenty button'''
        if len(fManager.L1.toPlainText()) == 1:
            fManager.New.setDisabled(0)
            fManager.Clear.setDisabled(0)
        elif len(fManager.L1.toPlainText()) == 0:
            fManager.New.setDisabled(1)
            fManager.Clear.setDisabled(1)

    def fillForm(self, row, column):
        '''fills in the fields with data from the subentry selected in the table list'''
        thisRow = self.table.item(row,column)
        self.FmData.currentCell = thisRow
        self.L1.setHtml(thisRow.data(35).findtext('L1'))
        if thisRow.data(35).findtext('L2'):
            self.L2.setHtml(thisRow.data(35).findtext('L2'))
        n = self.table.rowCount()
        self.orderEntries.setMaximum(n)
        self.orderEntries.setMinimum(1)
        self.orderEntries.setDisabled(0)
        self.FmData.currentSubentry = int(thisRow.data(35).attrib.get('Index'))
        self.orderEntries.setValue(int(thisRow.data(35).attrib.get('Index')))
        self.FmData.currentSubentry = self.orderEntries.value()
        print(etree.tostring(thisRow.data(35),encoding='unicode'))
        if thisRow.data(35).findtext('POS'):
            self.POS.setHtml(thisRow.data(35).findtext('POS'))
        else:
            self.POS.clear()
        if thisRow.data(35).findtext('Reg'):
            self.Reg.setHtml(thisRow.data(35).findtext('Reg'))
        else:
            self.Reg.clear()
        dNode = thisRow.data(35).find('Dia')
        try:
            dialect = dNode.attrib.get('Dialect')
            self.Dia.setHtml(dialect)
            if dNode.find('Alternative') != None:
                aNodeList = dNode.findall('Alternative')
                j = 0
                for aNode in aNodeList:
                    variant = " " + aNode.attrib.get('Variant')
                    alternative = " " + aNode.text
                    if j == 0:
                        entry = variant + alternative
                    else:
                        entry = entry + "; " + variant + alternative
                    j += 1
                self.Alternative.setHtml(entry)
        except AttributeError:
            self.Dia.clear()
            self.Alternative.clear()

        examples = thisRow.data(35).findall('Ln')
        if examples:
            self.Ln.setRowCount(len(examples))
            for j in range(0,len(examples)):
                egID = examples[j].attrib.get('LnRef')
                egElement = myapp.ui.dataIndex.exDict[egID]
                eg = '<i>' + egElement.findtext('Line') + '</i>'
                if len(egElement.findtext('L1Gloss')) != 0:
                    eg = eg + " ‘" + egElement.findtext('L1Gloss') + "’ (" #needs to allow for l2 option)
                else:
                    eg = eg + " ‘" + egElement.findtext('L2Gloss') + "’ (" 
                eg = eg + egElement.attrib.get('Spkr') + ")"
                eg = re.sub('{Italics}','',eg)
                eg = re.sub('{/Italics}','',eg)
                tableCell = QtGui.QTableWidgetItem(1002)
                tableCell.setTextAlignment(QtCore.Qt.TextWordWrap)
                tableCell.setText(eg)
                tableCell.setData(36, egID)
                self.Ln.setItem(j,0,tableCell)
                self.Ln.resizeRowToContents(j)
        else:
            self.Ln.clear()
            
        myapp.ui.dataIndex.unsavedEdit = 0
        a = self.Ln.selectedRanges()
        if len(a) != 0:
            self.Ln.setRangeSelected(a[0],0)

        self.New.setDisabled(1)
        self.Kill.setDisabled(0)
        self.Update.setDisabled(0)
        self.Clear.setDisabled(0)
        self.minusEgBtn.setDisabled(1)
        self.switchEgBtn.setDisabled(1)
            
    def fillTable(self):
        '''updates table with list of subentries'''
        child = self.FmData.child
        subentry = child.findall('Def')
        howMany = len(subentry)
        self.table.setRowCount(howMany)
        for i in range(0,len(subentry)):
          entry = ''
          dialect = ''
          variant = ''
          alternative = ''
          POS = subentry[i].findtext('POS')
          if POS:
              entry = "(" + POS + ") "
          dNode = subentry[i].find('Dia')
          if dNode != None:
              dialect = dNode.attrib.get('Dialect')
              entry = entry + " <i>" + dialect + "</i> "
              aNodeList = dNode.findall('Alternative')
              if len(aNodeList) != 0:
                  j = 0
                  for aNode in aNodeList:
                      variant = aNode.attrib.get('Variant')
                      alternative = aNode.text
                      if j == 0 and len(aNodeList) - 1 == 0:
                          entry = entry + "[" + variant + " " + alternative + "] "
                      elif j == 0:
                          entry = entry + "[" + variant + " " + alternative
                      elif j == len(aNodeList) - 1:
                          entry = entry + "; " + variant + " " + alternative + "] "
                      else:
                          entry = entry + "; " + variant + " " + alternative
                      j += 1
                          
          Reg = subentry[i].findtext('Reg')                          
          if Reg:
              entry = entry + "<i>" + Reg + "</i> "
          entry = entry + subentry[i].findtext('L1')
          entry = entry.replace('{Italics}','<i>')
          entry = entry.replace('{/Italics}','</i>')
          entry = entry.replace('{{','<')
          entry = entry.replace('}}','>')
          
          tableCell = QtGui.QTableWidgetItem(1002)
          tableCell.setData(35, subentry[i])
          tableCell.setText(entry)
          tableCell.setFlags(QtCore.Qt.ItemIsEnabled)
          self.table.setItem(i,0,tableCell)
          self.table.resizeRowToContents(i)

    def addEg(self):
        if self.orderEntries.value() == 0:
            return
        self.addEgDialog = QtGui.QInputDialog()
        self.addEgDialog.setLabelText('Enter Example IDRef.')
        result = self.addEgDialog.exec_()
        if result == 1:
            newExRef = self.addEgDialog.textValue()
            ##need to make sure the idref is valid
            if newExRef.startswith('EX') == False:
                newExRef = 'EX' + newExRef
            try:
                a = myapp.ui.dataIndex.exDict[newExRef]
            except KeyError:
                self.refBox = QtGui.QMessageBox()
                self.refBox.setIcon(QtGui.QMessageBox.Warning)
                self.refBox.setStandardButtons(QtGui.QMessageBox.Cancel)
                self.refBox.setStandardButtons(QtGui.QMessageBox.Ok)
                self.refBox.setDefaultButton(QtGui.QMessageBox.Ok)
                self.refBox.setText('IDRef error.')
                self.refBox.setInformativeText('"%s" is either not a valid<br />'
                                               'IDRef or the example it refers<br />'
                                               'to no longer exists.' %newExRef)
                self.refBox.exec_()
                return
            newElement = '<Ln LnRef="' + newExRef + '" />'
            newEg = etree.XML(newElement)
        else:
            return
        child = self.FmData.child
        whichDef = self.orderEntries.value()
        insertPoint = self.Ln.rowCount()
        elemList = list(child)
        for i in range(2,len(elemList)):
            if elemList[i].tag == 'Def':
                pointer = i
                break
        targetDef = whichDef + pointer
        l = list(child[targetDef-1])
        insertPoint += len(l)
        child[targetDef-1].insert(insertPoint,newEg)

        ##update Ln table
        j = self.orderEntries.value() - 1
        self.fillForm(j,0)

        self.editState.unsavedEdit = 1

    def minusEg(self):
        if self.Ln.rowCount() == 0:
            return
        try:
            thisCell = self.Ln.currentRow()
            egIndex = self.Ln.item(thisCell,0).data(36)
        except AttributeError:
            return
        child = self.FmData.child
        for Def in child.iter('Def'):
            tag = 'Ln[@LnRef="' + egIndex + '"]'
            badEg = Def.find(tag)
            if badEg != None:
                Def.remove(badEg)
                break
        self.Ln.removeRow(thisCell)

        FieldManager.editState.unsavedEdit = 1
        self.minusEgBtn.setDisabled(1)
        self.switchEgBtn.setDisabled(1)

    def newSubEntry(self):
        if len(self.L1.toPlainText()) == 0:
            return
        numSubs = self.table.rowCount() ##gets ordinal for subentry
        child = self.FmData.child
        elemList = list(child)
        for i in range(2,len(elemList)):
            if elemList[i].tag == 'Def':
                pointer = i
                break
        newSubIndex = numSubs + pointer
        defIndex = str(numSubs + 1)
        
        ##insert new <Def>
        child.insert(newSubIndex,etree.Element('Def',{'Index':defIndex}))
        optIndex = 0
         
        ##insert new POS
        if len(self.POS.toPlainText()) !=0:
            etree.SubElement(child[newSubIndex],'POS')
            tag = "Def[@Index='" + defIndex + "']/POS"
            child.find(tag).text = self.POS.toPlainText()
            optIndex += 1
       
        ##insert new Reg
        if len(self.Reg.toPlainText()) !=0:
            etree.SubElement(child[newSubIndex],'Reg')
            tag = "Def[@Index='" + defIndex + "']/Reg"
            child.find(tag).text = self.Reg.toPlainText()
            optIndex += 1
       
        ##insert new Dia
        if len(self.Dia.toPlainText()) !=0:
            dialect = self.Dia.toPlainText()
            etree.SubElement(child[newSubIndex],'Dia',{'Dialect':dialect})
            alternative = self.Alternative.toPlainText().split(None,1)
            ##need to check to make sure dialect is formatted correctly
            if len(alternative) == 1:
                self.formatBox()
                return
            variant = alternative[0]
            if variant.endswith('.') == False:
                variant += '.'
            ##find cross-refs
            crossRef = None
            for entry in myapp.ui.dataIndex.root.findall('Lex'):
                lexeme = entry.find('Orth').text
                if lexeme == alternative[1] and entry.attrib.get('Hom') != 0:
                    synList = item.attrib.get('Hom').split(", ")
                    synList.append(item.attrib.get('LexID'))
                    newCf = crossRefManager()
                    newCf.setRefs(synList)
                    if newCf.exec_():
                        crossRef = newCf.getRef()
                    else:
                        crossRef = None
                    break
                elif lexeme == alternative[1]:
                    crossRef = entry.attrib.get('LexID')
                    break
            
            if crossRef != None:
                etree.SubElement(child[newSubIndex][optIndex],'Alternative',{'Variant':variant, 'CrossRef':crossRef})
            else:
                etree.SubElement(child[newSubIndex][optIndex],'Alternative',{'Variant':variant})
            tag = "Def[@Index='" + defIndex + "']/Dia/Alternative"
            child.find(tag).text = alternative[1]
            optIndex += 1
       
       ##insert new L1
        etree.SubElement(child[newSubIndex],'L1')
        tag = "Def[@Index='" + defIndex + "']/L1"
        child.find(tag).text = self.L1.toPlainText()
        
        ##insert new L2
        etree.SubElement(child[newSubIndex],'L2')
        tag = "Def[@Index='" + defIndex + "']/L2"
        child.find(tag).text = self.L2.toPlainText()

        ##insert new <Ln> nodes
        for i in range(0,self.Ln.rowCount()):
            number = self.Ln.item(i,0).data(36)
            etree.SubElement(child[newSubIndex],'Ln',{'LnRef':number})                   
                      
        FieldManager.editState.unsavedEdit = 1
       
        ##update table on palette and activate spinbox
        self.fillTable()
        n = self.table.rowCount()
        self.orderEntries.setMaximum(n)
        n -= 1
        thisRow = self.table.item(n,0)
        self.orderEntries.setValue(int(thisRow.data(35).attrib.get('Index')))
        self.FmData.currentSubentry = self.orderEntries.value()
        self.orderEntries.setDisabled(0)
        self.Update.setDisabled(0)
                    
    def updateLexCard(self, child):
        cardLoader.loadDefinitions(child)

    def formatBox(self):
        self.formatBox = QtGui.QMessageBox()
        self.formatBox.setIcon(QtGui.QMessageBox.Warning)
        self.formatBox.setStandardButtons(QtGui.QMessageBox.Cancel)
        self.formatBox.setStandardButtons(QtGui.QMessageBox.Ok)
        self.formatBox.setDefaultButton(QtGui.QMessageBox.Ok)
        self.formatBox.setText('Formatting error.')
        self.formatBox.setInformativeText('The Alternative field must have both<br />'
                             'the abbreviated variant name and the <br />'
                             'alternative form, as in:'
                             '<blockquote><big>US soda</big></blockquote><br />'
                             'Separate multiple entries with a semi-colon.')
        self.formatBox.exec_()

    def cancelled(self,checked):
        myapp.ui.dataIndex.unsavedEdit = 0
        self.reject()

    def OK(self,checked):
        if FieldManager.editState.unsavedEdit != 0:
            self.saveBox = QtGui.QMessageBox()
            self.saveBox.setIcon(QtGui.QMessageBox.Question)
            self.saveBox.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
            self.saveBox.setDefaultButton(QtGui.QMessageBox.Save)
            self.saveBox.setText('Your entry has been modfiied.')
            self.saveBox.setInformativeText('Do you want to save your changes?')
            self.saveBox.exec_()
            if self.saveBox.result() == QtGui.QMessageBox.Discard:
                return
            elif self.saveBox.result() == QtGui.QMessageBox.Save:
                if self.orderEntries.value() != 0:
                    self.updateXML()
       
                ##save edits
                saveDoc = etree.tostring(myapp.ui.dataIndex.root, "unicode")
                saveFile = open(myapp.ui.dataIndex.sourceFile, "w", encoding = "UTF-8")
                saveFile.write(saveDoc)
                saveFile.close()
                FieldManager.editState.unsavedEdit = 0                   
                self.updateLexCard(self.FmData.child)
                self.accept()
        else:
            self.accept()

    def killSubentry(self):
        if len(self.L1.toPlainText()) == 0:
            return
        toUpdate = self.orderEntries.value() - 1  ##gets ordinal for subentry
        child = self.FmData.child
        elemList = list(child)
        for i in range(2,len(elemList)):
            if elemList[i].tag == 'Def':
                pointer = i
                break
        badDef = toUpdate + pointer
        badNode = elemList[badDef]
        child.remove(badNode)
        number = 0
        for Def in child.iter('Def'):
            number += 1
            Def.set('Index',str(number))
        self.orderEntries.setMinimum(0)
        self.orderEntries.setValue(0)
        self.orderEntries.setMaximum(self.orderEntries.maximum()-1)
        self.FmData.child = child

        ##clear fields
        self.clearAll()

        FieldManager.editState.unsavedEdit = 1

        ##update table on palette
        self.fillTable()
                
    def updateXML(self):
        if len(self.L1.toPlainText()) == 0:
            self.noDefBox = QtGui.QMessageBox()
            self.noDefBox.setIcon(QtGui.QMessageBox.Warning)
            self.noDefBox.setStandardButtons(QtGui.QMessageBox.Cancel)
            self.noDefBox.setStandardButtons(QtGui.QMessageBox.Ok)
            self.noDefBox.setDefaultButton(QtGui.QMessageBox.Ok)
            self.noDefBox.setText('No definition.')
            self.noDefBox.setInformativeText('You must have a definition<br />in the primary working language.')
            self.noDefBox.exec_()
            return
        toUpdate = self.orderEntries.value() - 1 ##gets ordinal for subentry
        child = self.FmData.child
        elemList = list(child)
        for i in range(0,len(elemList)):
            if elemList[i].tag == 'Def':
                pointer = i
                break
        upDateDef = toUpdate + pointer
        defIndex = str(toUpdate+1)
        oldDef = elemList[upDateDef]
        
        child.remove(oldDef)
        
        ##insert new <Def>
        child.insert(upDateDef,etree.Element('Def',{'Index':defIndex}))
        optIndex = 0
        
        ##insert new POS
        if len(self.POS.toPlainText()) !=0:
            newPOS = etree.SubElement(child[upDateDef],'POS')
            newPOS.text = self.POS.toPlainText()
            optIndex += 1
       
        ##insert new Reg
        if len(self.Reg.toPlainText()) !=0:
            newReg = etree.SubElement(child[upDateDef],'Reg')
            newReg.text = self.Reg.toPlainText()
            optIndex += 1
       
        ##insert new Dia
        if len(self.Dia.toPlainText()) !=0:
            crossRef = None
            dialect = self.Dia.toPlainText()
            etree.SubElement(child[upDateDef],'Dia',{'Dialect':dialect})
            if len(self.Alternative.toPlainText()) !=0:
                ##should probably check to ensure that there is a dialect specified and warn user if not##
                altList = self.Alternative.toPlainText().split("; ")
                for item in altList:
                    alternative = item.split(None,1)
                    if len(alternative) == 1:
                        self.formatBox()
                        return                  
                    variant = alternative[0]
                    if variant.endswith('.') == False:
                        variant += '.'
                    for item in myapp.ui.dataIndex.root.iter('Lex'):
                        lexeme = item.find('Orth').text
                        if lexeme == alternative[1] and item.attrib.get('Hom') != None:
                            synList = item.attrib.get('Hom').split(", ")
                            synList.append(item.attrib.get('LexID'))
                            newCf = crossRefManager()
                            newCf.setRefs(synList)
                            if newCf.exec_():
                                crossRef = newCf.getRef()
                            else:
                                crossRef = None
                            break
                        elif lexeme == alternative[1]:
                            crossRef = item.attrib.get('LexID')
                            break
                    if crossRef != None:
                        newAlt = etree.SubElement(child[upDateDef][optIndex],'Alternative',{'Variant':variant,'CrossRef':crossRef})
                    else:
                        newAlt = etree.SubElement(child[upDateDef][optIndex],'Alternative',{'Variant':variant})
                    newAlt.text = alternative[1]
       
       ##insert new L1
        newL1 = etree.SubElement(child[upDateDef],'L1')
        newL1.text = self.L1.toPlainText()
        
        ##insert new L2
        newL2 = etree.SubElement(child[upDateDef],'L2')
        newL2.text = self.L2.toPlainText()

        ##insert new <Ln> nodes
        for i in range(0,self.Ln.rowCount()):
            number = self.Ln.item(i,0).data(36)
            etree.SubElement(child[upDateDef],'Ln',{'LnRef':number})                   

        ##update lex card
        self.updateLexCard(child)
        
        ##update table on palette
        self.fillTable()                                  

    def clearAll(self):
        self.POS.clear()
        self.Reg.clear()
        self.Dia.clear()
        self.Alternative.clear()
        self.L1.clear()
        self.L2.clear()
        self.Ln.clear()
        self.orderEntries.setMinimum(0)
        self.orderEntries.setValue(0)
        self.FmData.currentSubentry = 0
        self.editState.unsavedEdit = 0
        self.New.setDisabled(1)
        self.Kill.setDisabled(1)
        self.Update.setDisabled(1)
        self.Clear.setDisabled(1)
        self.minusEgBtn.setDisabled(1)
        self.switchEgBtn.setDisabled(1)
        self.orderEntries.setDisabled(1)
              
    def retranslateUi(self, FieldManager):
        FieldManager.setWindowTitle(QtGui.QApplication.translate("FieldManager", "Update Definitions", None, QtGui.QApplication.UnicodeUTF8))
        self.Kill.setText(QtGui.QApplication.translate("FieldManager", "Del", None, QtGui.QApplication.UnicodeUTF8))
        self.Kill.setToolTip(QtGui.QApplication.translate("FieldManager", "delete selected subentry", None, QtGui.QApplication.UnicodeUTF8))
        self.New.setText(QtGui.QApplication.translate("FieldManager", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.New.setToolTip(QtGui.QApplication.translate("FieldManager", "add new subentry", None, QtGui.QApplication.UnicodeUTF8))
        self.Update.setText(QtGui.QApplication.translate("FieldManager", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.Update.setToolTip(QtGui.QApplication.translate("FieldManager", "save changes", None, QtGui.QApplication.UnicodeUTF8))
        self.Clear.setText(QtGui.QApplication.translate("FieldManager", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.Clear.setToolTip(QtGui.QApplication.translate("FieldManager", "clear all fields", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("FieldManager", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setToolTip(QtGui.QApplication.translate("FieldManager", "close window without saving changes", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setText(QtGui.QApplication.translate("FieldManager", "Okay", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setToolTip(QtGui.QApplication.translate("FieldManager", "close window and save changes", None, QtGui.QApplication.UnicodeUTF8))
        self.PLanguage.setText(QtGui.QApplication.translate("FieldManager", "Language", None, QtGui.QApplication.UnicodeUTF8))
        self.SLanguage.setText(QtGui.QApplication.translate("FieldManager", "Language", None, QtGui.QApplication.UnicodeUTF8))
        self.Speech.setText(QtGui.QApplication.translate("FieldManager", "Speech", None, QtGui.QApplication.UnicodeUTF8))
        self.addEgBtn.setText(QtGui.QApplication.translate("FieldManager", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.addEgBtn.setToolTip(QtGui.QApplication.translate("FieldManager", "add new example", None, QtGui.QApplication.UnicodeUTF8))
        self.minusEgBtn.setText(QtGui.QApplication.translate("FieldManager", "–", None, QtGui.QApplication.UnicodeUTF8))
        self.minusEgBtn.setToolTip(QtGui.QApplication.translate("FieldManager", "remove example", None, QtGui.QApplication.UnicodeUTF8))
        self.switchEgBtn.setText(QtGui.QApplication.translate("FieldManager", "Switch", None, QtGui.QApplication.UnicodeUTF8))
        self.switchEgBtn.setToolTip(QtGui.QApplication.translate("FieldManager", "move example to a different subentry", None, QtGui.QApplication.UnicodeUTF8))
        self.Part.setText(QtGui.QApplication.translate("FieldManager", "Part of", None, QtGui.QApplication.UnicodeUTF8))
        self.Register.setText(QtGui.QApplication.translate("FieldManager", "Register", None, QtGui.QApplication.UnicodeUTF8))
        self.Dialect.setText(QtGui.QApplication.translate("FieldManager", "Dialect", None, QtGui.QApplication.UnicodeUTF8))
        self.Primary.setText(QtGui.QApplication.translate("FieldManager", "Primary", None, QtGui.QApplication.UnicodeUTF8))
        self.Secondary.setText(QtGui.QApplication.translate("FieldManager", "Secondary", None, QtGui.QApplication.UnicodeUTF8))
        self.Examples.setText(QtGui.QApplication.translate("FieldManager", "Examples", None, QtGui.QApplication.UnicodeUTF8))
        self.AltLabel.setText(QtGui.QApplication.translate("FieldManager", "Alternative", None, QtGui.QApplication.UnicodeUTF8))
        self.orderEntries.setToolTip(QtGui.QApplication.translate("FieldManager", "move the selected subentry up or down in the list", None, QtGui.QApplication.UnicodeUTF8))
        self.POS.setToolTip(QtGui.QApplication.translate("FieldManager", "part of speech (if different <br />for this subentry)", None, QtGui.QApplication.UnicodeUTF8))
        self.Reg.setToolTip(QtGui.QApplication.translate("FieldManager", "register (if specific <br />to this subentry)", None, QtGui.QApplication.UnicodeUTF8))
        self.Dia.setToolTip(QtGui.QApplication.translate("FieldManager", "dialect (if specific <br />to this subentry)", None, QtGui.QApplication.UnicodeUTF8))
        self.Alternative.setToolTip(QtGui.QApplication.translate("FieldManager", "alternative form in other dialects.<br /> "
                                                                 "Use the format: US. soda. Separate <br />multiple entries with a semi-colon." , None, QtGui.QApplication.UnicodeUTF8))
        self.L1.setToolTip(QtGui.QApplication.translate("FieldManager", "definition in primary working language", None, QtGui.QApplication.UnicodeUTF8))
        self.L2.setToolTip(QtGui.QApplication.translate("FieldManager", "definition in secondary working language", None, QtGui.QApplication.UnicodeUTF8))


        ####BEGIN line splitter

class LineSplitter(QtGui.QDialog):
    '''class for splitting one example into two and feeding it back to other subroutines'''

    def __init__(self, parent=None):
        super(LineSplitter,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.setObjectName(_fromUtf8("LineSplitter"))
        self.resize(1100, 440)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)
        
        self.dataBox = QtGui.QGroupBox(self)
        self.dataBox.setGeometry(QtCore.QRect(10, 9, 1080, 380))
        self.dataBox.setObjectName(_fromUtf8("lexBox"))
        self.fLayout = QtGui.QFormLayout(self)
        self.firstLine = QtGui.QTextEdit()
        self.firstLine.setObjectName(_fromUtf8("firstLine"))
        self.firstLine.setFixedWidth(900)
        self.firstLine.setFixedHeight(25)
        self.secondLine = QtGui.QTextEdit()
        self.secondLine.setFixedWidth(900)
        self.secondLine.setFixedHeight(25)
        self.firstL1 = QtGui.QTextEdit()
        self.firstL1.setFixedWidth(900)
        self.firstL1.setFixedHeight(25)
        self.secondL1 = QtGui.QTextEdit()
        self.secondL1.setFixedWidth(900)
        self.secondL1.setFixedHeight(25)
        self.firstL2 = QtGui.QTextEdit()
        self.firstL2.setFixedWidth(900)
        self.firstL2.setFixedHeight(25)
        self.secondL2 = QtGui.QTextEdit()
        self.secondL2.setFixedWidth(900)
        self.secondL2.setFixedHeight(25)
        self.egArea = QtGui.QScrollArea()
        self.egArea.setFixedWidth(900)
        self.egTable = textTable(self.egArea)
        self.egTable.setFixedWidth(900)
        self.tableLabel = QtGui.QLabel()
        self.tableLabel.setText('Select the column where the new example begins by clicking on its number.')
        self.fLayout.addRow('First half (line)',self.firstLine)
        self.fLayout.addRow('Second half (line)',self.secondLine)
        self.fLayout.addRow('',self.egArea)
        self.fLayout.addRow('',self.tableLabel)
        self.fLayout.addRow('First half (gloss)',self.firstL1)
        self.fLayout.addRow('Second half (gloss)',self.secondL1)
        self.fLayout.addRow('First half (gloss)',self.firstL2)
        self.fLayout.addRow('Second half (gloss)',self.secondL2)
        self.dataBox.setLayout(self.fLayout)

        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 390, 1080, 56))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonBox.sizePolicy().hasHeightForWidth())
        self.ButtonBox.setSizePolicy(sizePolicy)
        self.ButtonBox.setTitle(_fromUtf8(""))
        self.ButtonBox.setFlat(True)
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ButtonBox)
        self.horizontalLayout.setObjectName(_fromUtf8("ButtonLayout"))
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.CancelBtn = QtGui.QPushButton(self.ButtonBox)
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)       
        self.horizontalLayout.addWidget(self.CancelBtn)
        self.OkayBtn = QtGui.QPushButton(self.ButtonBox)
        self.OkayBtn.setObjectName(_fromUtf8("OkayBtn"))
        self.OkayBtn.setDefault(1)
        self.horizontalLayout.addWidget(self.OkayBtn)
        self.OkayBtn.clicked.connect(self.OK)
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def cancelled(self,checked):
        self.reject()

    def OK(self,checked):
        if self.egTable.currentColumn() == -1:
            queryBox = QtGui.QMessageBox()
            queryBox.setIcon(QtGui.QMessageBox.Warning)
            queryBox.setStandardButtons(QtGui.QMessageBox.Ok)
            queryBox.setDefaultButton(QtGui.QMessageBox.Ok)
            queryBox.setText('No column selected!')
            queryBox.setInformativeText('Please indicate where the morphological analysis\n'
                                        'should be divided by selecting a column.')
            queryBox.exec_()
            return
        self.accept()

    def newData(self, oldID):
        line1 = self.firstLine.toPlainText()
        line2 = self.secondLine.toPlainText()
        gloss11 = self.firstL1.toPlainText()
        gloss12 = self.secondL1.toPlainText()
        if len(self.firstL2.toPlainText()) !=0:
            gloss21 = self.firstL2.toPlainText()
            gloss22 = self.secondL2.toPlainText()
        if self.egTable.columnCount() != 0:
            mrphList1 = []
            mrphList2 = []
            ilegList1 = []
            ilegList2 = []
            mrph1 = None
            mrph2 = None
            ileg1 = None
            ileg2 = None
            for i in range(0,self.egTable.currentColumn()):
                mrphList1.append(self.egTable.item(0,i).text())
                ilegList1.append(self.egTable.item(1,i).text())
            for i in range(self.egTable.currentColumn(),self.egTable.columnCount()):
                mrphList2.append(self.egTable.item(0,i).text())
                ilegList2.append(self.egTable.item(1,i).text())
            for item in mrphList1:
                if mrph1 == None:
                    mrph1 = item
                else:
                    mrph1 += '\t' + item
            for item in mrphList2:
                if mrph2 == None:
                    mrph2 = item
                else:
                    mrph2 += '\t' + item
            for item in ilegList1:
                if ileg1 == None:
                    ileg1 = item
                else:
                    ileg1 += '\t' + item
            for item in ilegList2:
                if ileg2 == None:
                    ileg2 = item
                else:
                    ileg2 += '\t' + item     
            ileg1 = ileg1.replace('<small>','{ABB}')
            ileg1 = ileg1.replace('</small>','{/ABB}')
            ileg1 = ileg1.replace('</small>','{{/ABB}}')
            ileg1 = ileg1.replace('<small>','{{ABB}}')
            ileg1 = ileg1.replace('<','{{')
            ileg1 = ileg1.replace('>','}}')
            ileg2 = ileg2.replace('<small>','{ABB}')
            ileg2 = ileg2.replace('</small>','{/ABB}')
            ileg2 = ileg2.replace('</small>','{{/ABB}}')
            ileg2 = ileg2.replace('<small>','{{ABB}}')
            ileg2 = ileg2.replace('<','{{')
            ileg2 = ileg2.replace('>','}}')
        update = QtCore.QDate.currentDate().toString(QtCore.Qt.ISODate)
        date = myapp.ui.tDate.toPlainText()
        spkr = myapp.ui.tSource.toPlainText()
        rschr = myapp.ui.tResearcher.toPlainText()
        #generate ID number for second node (should try to do this with the generateID method)
        codeList = sorted(myapp.ui.dataIndex.exDict.keys(), key=lambda i : int(i[2:]))
        topCode = int(codeList[-1][2:])
        topCode += 1
        ExID = 'EX' + str(topCode)
        while ExID in codeList:
            topCode += 1
            ExID = 'EX' + str(topCode)
        ##revised node
        for node in myapp.ui.dataIndex.root.iter('Ex'):
            if node.attrib.get('ExID') == oldID:
                node.find('Line').text = line1
                if self.egTable.columnCount() != 0:
                    node.find('Mrph').text = mrph1
                    node.find('ILEG').text = ileg1
                node.find('L1Gloss').text = gloss11
                node.find('L2Gloss').text = gloss21
                node.set('Update',update)
                break
        k = myapp.ui.dataIndex.root.find('Ex')
        d = myapp.ui.dataIndex.root.getchildren().index(k)
        ##new node
        node = etree.Element('Ex')
        etree.SubElement(node,'Line')
        node.find('Line').text = line2
        if self.egTable.columnCount() != 0:
            etree.SubElement(node,'Mrph')
            etree.SubElement(node,'ILEG')
            node.find('Mrph').text = mrph2
            node.find('ILEG').text = ileg2
        etree.SubElement(node,'L1Gloss')
        node.find('L1Gloss').text = gloss12
        etree.SubElement(node,'L2Gloss')
        node.find('L2Gloss').text = gloss22
        node.set('Date',date)
        node.set('Update',update)
        node.set('Spkr',spkr)
        node.set('Rschr',rschr)
        node.set('ExID',ExID)
        node.set('SourceText',myapp.ui.dataIndex.currentCard)
        myapp.ui.dataIndex.root.insert(d,node)
        myapp.ui.dataIndex.exDict[ExID] = node
        idList = [oldID,ExID]
        return idList
        
    def fillForm(self,exID):
        node = myapp.ui.dataIndex.exDict[exID]
        self.firstLine.setHtml(node.find('Line').text)
        self.firstL1.setHtml(node.find('L1Gloss').text)
        if node.find('L2Gloss').text != None:
            self.firstL2.setHtml(node.find('L2Gloss').text)
        self.egTable.horizontalHeader().show()
        self.egTable.horizontalHeader().setEnabled(1)
        if node.find('Mrph') != None:
            entryRow1 = node.findtext('Mrph').split('\t')
            entryRow2 = node.findtext('ILEG').split('\t')
            self.egTable.setRowCount(2)
            self.egTable.setColumnCount(len(entryRow1))
            self.egTable.setRowHeight(0,20)
            self.egTable.setRowHeight(1,20)
            for i in range(len(entryRow1)):
              parse = entryRow2[i].replace('{ABB}','<small>')
              parse = parse.replace('{/ABB}','</small>')
              parse = parse.replace('{{/ABB}}','</small>')
              parse = parse.replace('{{ABB}}','<small>')
              parse = parse.replace('{{','<')
              parse = parse.replace('}}','>')
              tableCellTop = QtGui.QTableWidgetItem(10001)
              tableCellTop.setText(entryRow1[i])
              self.egTable.setItem(0,i,tableCellTop)
              tableCellBottom = QtGui.QTableWidgetItem(10001)
              tableCellBottom.setText(parse + " ")
              tableCellBottom.setTextAlignment(QtCore.Qt.AlignBottom)
              self.egTable.setItem(1,i,tableCellBottom)
              self.egTable.resizeColumnToContents(i)            

    def retranslateUi(self, LineSplitter):
        LineSplitter.setWindowTitle(QtGui.QApplication.translate("LineSplitter", "Line splitter", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("LineSplitter", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setToolTip(QtGui.QApplication.translate("LineSplitter", "close window without saving", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setText(QtGui.QApplication.translate("LineSplitter", "Okay", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setToolTip(QtGui.QApplication.translate("LineSplitter", "close window and save changes", None, QtGui.QApplication.UnicodeUTF8))
        

        ###BEGIN media manager

class MediaManager(QtGui.QDialog):
    '''class for setting metadata for recorded media'''

    class focusOutFilter(QtCore.QObject):
      def __init__(self, parent=None):
        super(MediaManager.focusOutFilter, self).__init__(parent)
      
      def eventFilter(self, object, event):
          if event.type() == QtCore.QEvent.FocusOut:
            try:
                object.clearSelection()
            except AttributeError:
                pass
          return False
            
    class paletteField(QtGui.QTextEdit):
        def __init__(self, parent):
            super(MediaManager.paletteField, self).__init__(parent)
            self.filter = MediaManager.focusOutFilter()
            self.installEventFilter(self.filter)
            self.textChanged.connect(self.flagUnsavedEdits)

        def flagUnsavedEdits(self):
            myapp.ui.dataIndex.unsavedEdit = 1
                          
    def __init__(self, parent=None):
        super(MediaManager,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.setObjectName(_fromUtf8("MediaManager"))
        self.resize(350, 470)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)
        
        self.lexBox = QtGui.QGroupBox(self)
        self.lexBox.setGeometry(QtCore.QRect(10, 9, 330, 400))
        self.lexBox.setObjectName(_fromUtf8("lexBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.lexBox)
        self.verticalLayout.setObjectName(_fromUtf8("VerticalLayout"))
        self.topRowLayout = QtGui.QHBoxLayout()
        self.topRowLayout.setObjectName(_fromUtf8("topRowLayout"))
        self.topRowLayout.setAlignment(QtCore.Qt.AlignBottom)
        
        self.cell0Layout = QtGui.QVBoxLayout()
        self.speakerLabel = QtGui.QLabel(parent=None)
        self.speakerLabel.setObjectName(_fromUtf8("SpkrLabel"))
        self.cell0Layout.addWidget(self.speakerLabel,0)
        self.speakerCode = QtGui.QComboBox()
        self.speakerCode.setObjectName(_fromUtf8("SpeakerCode"))
        self.speakerCode.setFixedHeight(30)
        self.speakerCode.setFixedWidth(80)
        self.speakerCode.activated.connect(self.setSpeaker)
        self.cell0Layout.addWidget(self.speakerCode,1)
        self.topRowLayout.addLayout(self.cell0Layout,0)
       
        self.cell1Layout = QtGui.QVBoxLayout()
        self.rschrLabel = QtGui.QLabel(parent=None)
        self.rschrLabel.setObjectName(_fromUtf8("RschrLabel"))
        self.cell1Layout.addWidget(self.rschrLabel,0)
        self.researcherCode = QtGui.QComboBox()
        self.researcherCode.setObjectName(_fromUtf8("SpeakerCode"))
        self.researcherCode.setFixedHeight(30)
        self.researcherCode.setFixedWidth(80)
        self.researcherCode.activated.connect(self.setRschr)
        self.cell1Layout.addWidget(self.researcherCode,1)
        self.topRowLayout.addLayout(self.cell1Layout,1)
        
        self.cell2Layout = QtGui.QVBoxLayout()
        self.dateLabel = QtGui.QLabel(parent=None)
        self.dateLabel.setObjectName(_fromUtf8("DateLabel"))
        self.cell2Layout.addWidget(self.dateLabel,0)
        self.date = QtGui.QDateEdit()
        self.date.setFixedWidth(120)
        self.date.setDisplayFormat('yyyy-MM-dd')
        self.date.setObjectName(_fromUtf8("Date"))
        self.date.setFixedHeight(30)
        self.date.dateChanged.connect(self.setDate)
        self.cell2Layout.addWidget(self.date,1)
        self.topRowLayout.addLayout(self.cell2Layout,2)
        self.verticalLayout.addLayout(self.topRowLayout,0)
        
        self.cellA0Layout = QtGui.QVBoxLayout()
        self.placeLabel = QtGui.QLabel(parent=None)
        self.placeLabel.setObjectName(_fromUtf8("placeLabel"))
        self.cellA0Layout.addWidget(self.placeLabel,0)
        self.place = self.paletteField(parent=None)
        self.place.setObjectName(_fromUtf8("place"))
        self.place.setFixedHeight(30)
        self.cellA0Layout.addWidget(self.place,1)
        self.verticalLayout.addLayout(self.cellA0Layout,1)

        self.cellB0Layout = QtGui.QVBoxLayout()
        self.apparatusLabel = QtGui.QLabel(parent=None)
        self.apparatusLabel.setObjectName(_fromUtf8("AptLabel"))
        self.cellB0Layout.addWidget(self.apparatusLabel,0)
        self.apparatus = self.paletteField(parent=None)
        self.apparatus.setObjectName(_fromUtf8("Apparatus"))
        self.apparatus.setFixedHeight(30)
        self.cellB0Layout.addWidget(self.apparatus,1)
        self.verticalLayout.addLayout(self.cellB0Layout,2)

        self.cellB2Layout = QtGui.QVBoxLayout()
        self.typeLabel = QtGui.QLabel(parent=None)
        self.typeLabel.setObjectName(_fromUtf8("TypeLabel"))
        self.cellB2Layout.addWidget(self.typeLabel,0)
        self.type = self.paletteField(parent=None)
        self.type.setObjectName(_fromUtf8("FileType"))
        self.type.setFixedHeight(30)
        self.cellB2Layout.addWidget(self.type, 1)
        self.verticalLayout.addLayout(self.cellB2Layout,3)

        self.cellB1Layout = QtGui.QVBoxLayout()
        self.catalogLabel = QtGui.QLabel(parent=None)
        self.catalogLabel.setObjectName(_fromUtf8("CatLabel"))
        self.cellB1Layout.addWidget(self.catalogLabel,0)
        self.catalog = self.paletteField(parent=None)
        self.catalog.setObjectName(_fromUtf8("Catalogue"))
        self.catalog.setFixedHeight(30)
        self.cellB1Layout.addWidget(self.catalog, 1)
        self.verticalLayout.addLayout(self.cellB1Layout,4)
        
        self.bottomRowLayout = QtGui.QVBoxLayout()
        self.commentsLabel = QtGui.QLabel(parent=None)
        self.commentsLabel.setObjectName(_fromUtf8("CmtLabel"))
        self.bottomRowLayout.addWidget(self.commentsLabel,0)
        self.comments = self.paletteField(parent=None)
        self.comments.setObjectName(_fromUtf8("Comments"))
        self.comments.setFixedHeight(40)
        self.bottomRowLayout.addWidget(self.comments,1)
        self.verticalLayout.addLayout(self.bottomRowLayout,5)        

        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 415, 330, 56))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonBox.sizePolicy().hasHeightForWidth())
        self.ButtonBox.setSizePolicy(sizePolicy)
        self.ButtonBox.setTitle(_fromUtf8(""))
        self.ButtonBox.setFlat(True)
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ButtonBox)
        self.horizontalLayout.setObjectName(_fromUtf8("ButtonLayout"))
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.Clear = QtGui.QPushButton(self.ButtonBox)
        self.Clear.setObjectName(_fromUtf8("Clear"))
        self.Clear.clicked.connect(self.clearAll)
        self.horizontalLayout.addWidget(self.Clear)
        self.CancelBtn = QtGui.QPushButton(self.ButtonBox)
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)       
        self.horizontalLayout.addWidget(self.CancelBtn)
        self.OkayBtn = QtGui.QPushButton(self.ButtonBox)
        self.OkayBtn.setObjectName(_fromUtf8("OkayBtn"))
        self.OkayBtn.setDefault(1)
        self.horizontalLayout.addWidget(self.OkayBtn)
        self.OkayBtn.clicked.connect(self.OK)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        codeList = sorted(myapp.ui.dataIndex.speakerDict.keys())
        for index,item in enumerate(codeList):
            fullName = myapp.ui.dataIndex.speakerDict.get(item).findtext('Name')
            item += ' (' + fullName + ')'
            codeList[index] = item
        self.speakerCode.insertItems(0,codeList)
        if myapp.ui.dataIndex.lastSpeaker:
            j = self.speakerCode.findText(myapp.ui.dataIndex.lastSpeaker,QtCore.Qt.MatchStartsWith)
            self.speakerCode.setCurrentIndex(j)        
        
        codeList = sorted(myapp.ui.dataIndex.rschrDict.keys())
        self.researcherCode.insertItems(0,codeList)                                
        if myapp.ui.dataIndex.lastRschr:
            j = self.researcherCode.findText(myapp.ui.dataIndex.lastRschr,QtCore.Qt.MatchExactly)
            self.researcherCode.setCurrentIndex(j)
            
        if myapp.ui.dataIndex.lastDate:
            self.date.setDateTime(myapp.ui.dataIndex.lastDate)

        if myapp.ui.dataIndex.lastApparatus:
            self.apparatus.setText(myapp.ui.dataIndex.lastApparatus)
          
        if myapp.ui.dataIndex.lastPlace:
            self.place.setText(myapp.ui.dataIndex.lastPlace)
          
        if myapp.ui.dataIndex.lastFileFormat:
            self.type.setText(myapp.ui.dataIndex.lastFileFormat)
          
    def setDate(self):
        myapp.ui.dataIndex.lastDate = self.date.dateTime()
        myapp.ui.dataIndex.unsavedEdit = 1
        
    def setSpeaker(self):
        lastSpeaker = self.speakerCode.currentText().split(None,1)
        myapp.ui.dataIndex.lastSpeaker = lastSpeaker[0]
        myapp.ui.dataIndex.unsavedEdit = 1

    def setRschr(self):
        lastRschr = self.researcherCode.currentText().split(None,1)
        myapp.ui.dataIndex.lastRschr = lastRschr[0]
        myapp.ui.dataIndex.unsavedEdit = 1

    def setValues(self, mediaNode):
        for child in myapp.ui.dataIndex.root.iter('Media'):
            if child.attrib.get('MedID') == mediaNode:
                attribDict = child.attrib
                if 'Spkr' in attribDict and len(attribDict['Spkr']) != 0:
                    sNode = myapp.ui.dataIndex.speakerDict[attribDict['Spkr']]
                    fullName = attribDict['Spkr'] + ' (' + sNode.find('Name').text + ')'
                    l = self.speakerCode.findText(fullName,QtCore.Qt.MatchExactly)
                    self.speakerCode.setCurrentIndex(l)
                    
                if 'Rschr' in attribDict and len(attribDict['Rschr']) != 0:
                    l = self.researcherCode.findText(attribDict['Rschr'],QtCore.Qt.MatchExactly)
                    self.researcherCode.setCurrentIndex(l)

                if 'Date' in attribDict and len(attribDict['Date']) != 0:
                    self.date.setDateTime(self.date.dateTimeFromText(attribDict['Date']))
                    
                if 'Place' in attribDict and len(attribDict['Place']) != 0:
                    self.place.setText(attribDict['Place'])

                if 'FileType' in attribDict and len(attribDict['FileType']) != 0:
                    self.type.setText(attribDict['FileType'])

                if 'Catalog' in attribDict and len(attribDict['Catalog']) != 0:
                    self.catalog.setText(attribDict['Catalog'])

                if 'Apparatus' in attribDict and len(attribDict['Apparatus']) != 0:
                    self.apparatus.setText(attribDict['Apparatus'])

                if child.find('Comments') != None:
                    self.comments.setText(child.findtext('Comments'))
                break

    def getValues(self):
        metaData = []
        speaker = self.speakerCode.currentText().split(None,1)
        metaData.append(speaker[0])
        metaData.append(self.researcherCode.currentText())
        metaData.append(self.date.textFromDateTime(self.date.dateTime()))
        metaData.append(self.apparatus.toPlainText())
        metaData.append(self.catalog.toPlainText())
        metaData.append(self.comments.toPlainText())
        metaData.append(self.type.toPlainText())
        metaData.append(self.place.toPlainText())
        return metaData

    def renameWindow(self,fileName):
        self.setWindowTitle(QtGui.QApplication.translate("MediaManager", "Metadata: %s" %fileName, None, QtGui.QApplication.UnicodeUTF8))
        
    def cancelled(self,checked):
        self.reject()

    def OK(self,checked):
        myapp.ui.dataIndex.lastApparatus = self.apparatus.toPlainText()
        myapp.ui.dataIndex.lastPlace = self.place.toPlainText()
        myapp.ui.dataIndex.lastFileFormat = self.type.toPlainText()
        self.accept()
                
    def clearAll(self):
        self.apparatus.clear()
        self.catalog.clear()
        self.type.clear()
        self.place.clear()
        self.comments.clear()
              
    def retranslateUi(self, MediaManager):
        MediaManager.setWindowTitle(QtGui.QApplication.translate("MediaManager", "Recording metadata", None, QtGui.QApplication.UnicodeUTF8))
        self.Clear.setText(QtGui.QApplication.translate("MediaManager", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.Clear.setToolTip(QtGui.QApplication.translate("MediaManager", "clear all fields", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("MediaManager", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setToolTip(QtGui.QApplication.translate("MediaManager", "close window without saving", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setText(QtGui.QApplication.translate("MediaManager", "Okay", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setToolTip(QtGui.QApplication.translate("MediaManager", "close window and save changes", None, QtGui.QApplication.UnicodeUTF8))
        self.catalogLabel.setText(QtGui.QApplication.translate("MediaManager", "Catalogue info:", None, QtGui.QApplication.UnicodeUTF8))
        self.speakerLabel.setText(QtGui.QApplication.translate("MediaManager", "Consultant:", None, QtGui.QApplication.UnicodeUTF8))
        self.rschrLabel.setText(QtGui.QApplication.translate("MediaManager", "Researcher:", None, QtGui.QApplication.UnicodeUTF8))
        self.dateLabel.setText(QtGui.QApplication.translate("MediaManager", "Date recorded:", None, QtGui.QApplication.UnicodeUTF8))
        self.apparatusLabel.setText(QtGui.QApplication.translate("MediaManager", "Recording device:", None, QtGui.QApplication.UnicodeUTF8))
        self.commentsLabel.setText(QtGui.QApplication.translate("MediaManager", "Comments:", None, QtGui.QApplication.UnicodeUTF8))
        self.typeLabel.setText(QtGui.QApplication.translate("MediaManager", "File type:", None, QtGui.QApplication.UnicodeUTF8))
        self.speakerCode.setToolTip(QtGui.QApplication.translate("MediaManager", "consultant who was recorded", None, QtGui.QApplication.UnicodeUTF8))
        self.researcherCode.setToolTip(QtGui.QApplication.translate("MediaManager", "researcher who made the recording", None, QtGui.QApplication.UnicodeUTF8))
        self.date.setToolTip(QtGui.QApplication.translate("MediaManager", "date recorded", None, QtGui.QApplication.UnicodeUTF8))
        self.apparatus.setToolTip(QtGui.QApplication.translate("MediaManager", "recording device used", None, QtGui.QApplication.UnicodeUTF8))
        self.type.setToolTip(QtGui.QApplication.translate("MediaManager", "data file format", None, QtGui.QApplication.UnicodeUTF8))
        self.catalog.setToolTip(QtGui.QApplication.translate("MediaManager", "location of archived original recording", None, QtGui.QApplication.UnicodeUTF8))
        self.comments.setToolTip(QtGui.QApplication.translate("MediaManager", "comments", None, QtGui.QApplication.UnicodeUTF8))
        self.placeLabel.setText(QtGui.QApplication.translate("MediaManager", "Place:", None, QtGui.QApplication.UnicodeUTF8))
        self.place.setToolTip(QtGui.QApplication.translate("MediaManager", "place where recording was made", None, QtGui.QApplication.UnicodeUTF8))

        ##### END MediaManager####

        #### BEGIN crossRef Manager####
                                       
class crossRefManager(QtGui.QDialog):
    '''class for managing cross-references when they can't be generated automatically'''

    def __init__(self, parent=None):
        super(crossRefManager,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.setObjectName(_fromUtf8("crossRefManager"))
        self.resize(350, 400)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)

        self.refsBox = QtGui.QGroupBox(self)
        self.refsBox.setGeometry(QtCore.QRect(10, 9, 330, 325))
        self.refsBox.setObjectName(_fromUtf8("refsBox"))
        self.refList = QtGui.QListWidget(self.refsBox)
        self.refList.setGeometry(8,8,313,308)
        
        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 340, 330, 56))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonBox.sizePolicy().hasHeightForWidth())
        self.ButtonBox.setSizePolicy(sizePolicy)
        self.ButtonBox.setTitle(_fromUtf8(""))
        self.ButtonBox.setFlat(True)
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ButtonBox)
        self.horizontalLayout.setObjectName(_fromUtf8("ButtonLayout"))
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.CancelBtn = QtGui.QPushButton(self.ButtonBox)
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)       
        self.horizontalLayout.addWidget(self.CancelBtn)
        self.OkayBtn = QtGui.QPushButton(self.ButtonBox)
        self.OkayBtn.setObjectName(_fromUtf8("OkayBtn"))
        self.OkayBtn.setDefault(1)
        self.horizontalLayout.addWidget(self.OkayBtn)
        self.OkayBtn.clicked.connect(self.ok)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def setRefs(self,synList):
        j = 0
        for item in synList:
            node = myapp.ui.dataIndex.lexDict[item]
            linkText = node.findtext('Orth') + " (" + node.findtext('POS') + ") " + node.findtext('Def/L1')
            listItem = QtGui.QListWidgetItem()
            listItem.setText(linkText)
            listItem.setData(34,item)
            self.refList.insertItem(j,listItem)
            j += 1

    def getRef(self):
        crossRef=self.refList.currentItem().data(34)
        return crossRef

    def ok(self):
        self.accept()

    def cancelled(self,checked):
        self.reject()

    def retranslateUi(self, crossRefManager):
        crossRefManager.setWindowTitle(QtGui.QApplication.translate("crossRefManager", "Cross-reference manager", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("crossRefManager", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setToolTip(QtGui.QApplication.translate("crossRefManager", "close window without saving", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setText(QtGui.QApplication.translate("crossRefManager", "Okay", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setToolTip(QtGui.QApplication.translate("crossRefManager", "close window and save changes", None, QtGui.QApplication.UnicodeUTF8))

        #### BEGIN abbreviations Manager####
                                       
class abbrManager(QtGui.QDialog):
    '''class for managing abbreviations'''

    def __init__(self, parent=None):
        super(abbrManager,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.setObjectName(_fromUtf8("abbrManager"))
        self.resize(350, 200)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)

        self.refsBox = QtGui.QGroupBox(self)
        self.refsBox.setStyleSheet("{ font-size: 10px; }")
        self.refsBox.setGeometry(QtCore.QRect(10, 9, 330, 125))
        self.refsBox.setObjectName(_fromUtf8("refsBox"))
        self.fLayout = QtGui.QFormLayout(self)
        self.abbreviation = QtGui.QTextEdit()
        self.abbreviation.setObjectName(_fromUtf8("Abbreviation"))
        self.abbreviation.setFixedWidth(200)
        self.abbreviation.setFixedHeight(25)
        self.gloss = QtGui.QTextEdit()
        self.gloss.setObjectName(_fromUtf8("Gloss"))
        self.gloss.setFixedWidth(200)
        self.gloss.setFixedHeight(25)
        self.form = QtGui.QTextEdit()
        self.form.setObjectName(_fromUtf8("Form"))
        self.form.setFixedWidth(200)
        self.form.setFixedHeight(25)
        self.fLayout.addRow('Abbreviation',self.abbreviation)
        self.fLayout.addRow('Gloss',self.gloss)
        self.fLayout.addRow('Full form',self.form)
        self.refsBox.setLayout(self.fLayout)
       
        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 145, 330, 56))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonBox.sizePolicy().hasHeightForWidth())
        self.ButtonBox.setSizePolicy(sizePolicy)
        self.ButtonBox.setTitle(_fromUtf8(""))
        self.ButtonBox.setFlat(True)
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ButtonBox)
        self.horizontalLayout.setObjectName(_fromUtf8("ButtonLayout"))
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.CancelBtn = QtGui.QPushButton(self.ButtonBox)
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)       
        self.horizontalLayout.addWidget(self.CancelBtn)
        self.OkayBtn = QtGui.QPushButton(self.ButtonBox)
        self.OkayBtn.setObjectName(_fromUtf8("OkayBtn"))
        self.OkayBtn.setDefault(1)
        self.horizontalLayout.addWidget(self.OkayBtn)
        self.OkayBtn.clicked.connect(self.ok)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def setAbbr(self,abvNode):
        self.abbreviation.setHtml(abvNode.attrib.get('Abv'))
        self.gloss.setHtml(abvNode.attrib.get('Term'))
        try:
            self.form.setHtml(abvNode.attrib.get('Form'))
        except AttributeError:
            pass

    def setData(self):
        if len(self.abbreviation.toPlainText()) != 0 and len(self.gloss.toPlainText()) != 0:
            dataList = [self.abbreviation.toPlainText(),self.gloss.toPlainText()]
            if len(self.form.toPlainText()) != 0:
                dataList.append(self.form.toPlainText())
            else:
                dataList.append(None)
        else:
            queryBox = QtGui.QMessageBox()
            queryBox.setIcon(QtGui.QMessageBox.Warning)
            queryBox.setStandardButtons(QtGui.QMessageBox.Ok)
            queryBox.setDefaultButton(QtGui.QMessageBox.Ok)
            queryBox.setText('Please give an abbreviation\nand a gloss.')
            queryBox.exec_()
            return
        return dataList

    def ok(self):
        self.accept()

    def cancelled(self,checked):
        self.reject()

    def retranslateUi(self, abbrManager):
        abbrManager.setWindowTitle(QtGui.QApplication.translate("abbrManager", "Abbreviations", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("abbrManager", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setToolTip(QtGui.QApplication.translate("abbrManager", "close window without saving", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setText(QtGui.QApplication.translate("abbrManager", "Okay", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setToolTip(QtGui.QApplication.translate("abbrManager", "close window and save changes", None, QtGui.QApplication.UnicodeUTF8))
        self.abbreviation.setToolTip(QtGui.QApplication.translate("abbrManager", "new abbreviation", None, QtGui.QApplication.UnicodeUTF8))
        self.gloss.setToolTip(QtGui.QApplication.translate("abbrManager", "new gloss", None, QtGui.QApplication.UnicodeUTF8))
        self.form.setToolTip(QtGui.QApplication.translate("abbrManager", "full or underlying form", None, QtGui.QApplication.UnicodeUTF8))

        ###BEGIN grammar manager

class GrammarManager(QtGui.QDialog):
    '''class for constraining user input to lexicon grammar fields'''

    class focusOutFilter(QtCore.QObject):
        def __init__(self, parent=None):
            super(GrammarManager.focusOutFilter, self).__init__(parent)

        def eventFilter(self, object, event):
            if event.type() == QtCore.QEvent.FocusIn:
                try:
                    gManager.addEgBtn.setEnabled(0)
                    gManager.delEgBtn.setEnabled(0)
                    gManager.Add.setEnabled(1)
                    gManager.Del.setEnabled(0)
                    gManager.recordings.clear()
                    gManager.soundFileMeta.clear()
                    gManager.trackTable.whichTable = ''
                except AttributeError:
                    pass
            if event.type() == QtCore.QEvent.FocusOut:
                try:
                    object.clearSelection()
                except AttributeError:
                    pass
            return False
            
    class paletteField(QtGui.QTextEdit):
        def __init__(self, parent):
            super(GrammarManager.paletteField, self).__init__(parent)
            self.filter = GrammarManager.focusOutFilter()
            self.installEventFilter(self.filter)
            self.textChanged.connect(self.flagUnsavedEdits)

        def flagUnsavedEdits(self):
            myapp.ui.dataIndex.unsavedEdit = 1

                          
    class grmTable(QtGui.QTableWidget):
        def __init__(self, parent):
            super(GrammarManager.grmTable, self).__init__(parent)
            self.setStyleSheet("selection-background-color: #F0F0F0;")
            delegate = HTMLDelegate()
            self.setItemDelegate(delegate)
            self.cellClicked.connect(self.clickedCell)
            self.filter = GrammarManager.focusOutFilter()
            self.installEventFilter(self.filter)
            if myapp.ui.dataIndex.unsavedEdit == 0:
                self.cellChanged.connect(self.flagUnsavedEdits)

        def clickedCell(self,row,column):
            gManager.trackTable.whichTable = self.sender()
            GrammarManager.selectElement(self,gManager.trackTable.whichTable)

        def flagUnsavedEdits(self):
            myapp.ui.dataIndex.unsavedEdit = 1

    class trackTable:
        whichTable = ''

    def __init__(self, parent=None):
        super(GrammarManager,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.setObjectName(_fromUtf8("GrammarManager"))
        self.resize(430, 483)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)
        self.setStyleSheet("QGroupBox {\n margins: 0px;\n}")
        
        self.lexBox = QtGui.QGroupBox(self)
        self.lexBox.setGeometry(QtCore.QRect(10, 9, 410, 386))
        self.lexBox.setObjectName(_fromUtf8("lexBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.lexBox)
        self.verticalLayout.setObjectName(_fromUtf8("VerticalLayout"))

        self.cell0Layout = QtGui.QVBoxLayout()
        self.grammarLabel = QtGui.QLabel(parent=None)
        self.grammarLabel.setObjectName(_fromUtf8("grammarLabel"))
        self.cell0Layout.addWidget(self.grammarLabel,0)
        self.grammar = self.grmTable(parent=None)
        self.grammar.setFixedHeight(137)
        self.grammar.setRowCount(0)
        self.grammar.horizontalHeader().setEnabled(0)
        self.grammar.horizontalHeader().hide()
        self.grammar.verticalHeader().setEnabled(0)
        self.grammar.verticalHeader().hide()
        self.grammar.setColumnCount(2)
        self.grammar.setColumnWidth(0,30)
        self.grammar.setColumnWidth(1,348)
        self.grammar.setSortingEnabled(1)
        self.grammar.setObjectName(_fromUtf8("grammar"))
        self.cell0Layout.addWidget(self.grammar,1)
        self.verticalLayout.addLayout(self.cell0Layout,0)

        self.cell1Layout = QtGui.QVBoxLayout()
        self.C2Label = QtGui.QLabel(parent=None)
        self.C2Label.setObjectName(_fromUtf8("C2Label"))
        self.cell1Layout.addWidget(self.C2Label,0)
        self.C2 = self.grmTable(parent=None)
        self.C2.setFixedHeight(92)
        self.C2.setRowCount(0)
        self.C2.horizontalHeader().setEnabled(0)
        self.C2.horizontalHeader().hide()
        self.C2.verticalHeader().setEnabled(0)
        self.C2.verticalHeader().hide()
        self.C2.setColumnCount(1)
        self.C2.setColumnWidth(0,410)
        self.C2.setSortingEnabled(0)
        self.C2.setObjectName(_fromUtf8("C2"))
        self.cell1Layout.addWidget(self.C2,1)
        self.verticalLayout.addLayout(self.cell1Layout,1)

        self.cell2Layout = QtGui.QVBoxLayout()
        self.cfLabel = QtGui.QLabel(parent=None)
        self.cfLabel.setObjectName(_fromUtf8("TypeLabel"))
        self.cell2Layout.addWidget(self.cfLabel,0)
        self.cf = self.paletteField(parent=None)
        self.cf.setObjectName(_fromUtf8("FileType"))
        self.cf.setFixedHeight(30)
        self.cell2Layout.addWidget(self.cf, 1)
        self.verticalLayout.addLayout(self.cell2Layout,2)

        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 401, 410, 106))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonBox.sizePolicy().hasHeightForWidth())
        self.ButtonBox.setSizePolicy(sizePolicy)
        self.ButtonBox.setTitle(_fromUtf8(""))
        self.ButtonBox.setFlat(True)
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        
        self.soundBox = QtGui.QGroupBox(self.ButtonBox)
        self.soundBox.setGeometry(QtCore.QRect(0, 9, 146, 65))
        self.soundBox.setFixedWidth(146)
        self.soundBox.setStyleSheet(_fromUtf8("QToolButton {\n"
"    background: auto;\n margins: 0px;\n"
"}"))
        self.soundBox.setObjectName(_fromUtf8("soundBox"))
        self.recordings = QtGui.QComboBox(self.soundBox)
        self.recordings.setGeometry(QtCore.QRect(5, 5, 101, 32))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.recordings.setFont(font)
        self.recordings.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        self.recordings.setObjectName(_fromUtf8("recordings"))
        self.playSoundBtn = QtGui.QToolButton(self.soundBox)
        self.playSoundBtn.setGeometry(QtCore.QRect(112, 8, 27, 23))
        self.playSoundBtn.setStyleSheet(_fromUtf8("QToolButton {\n"
"    border-image: url(:/new/SpeakerBtn.png);\n"
"}"))
        self.playSoundBtn.setText(_fromUtf8(""))
        self.playSoundBtn.setObjectName(_fromUtf8("playSoundBtn"))
        self.playSoundBtn.clicked.connect(self.playSound)
        self.soundFileMeta = QtGui.QLabel(self.soundBox)
        self.soundFileMeta.setGeometry(QtCore.QRect(5, 40, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.soundFileMeta.setFont(font)
        self.soundFileMeta.setStyleSheet(_fromUtf8(""))
        self.soundFileMeta.setObjectName(_fromUtf8("soundFileMeta"))
        self.soundMetaBtn = QtGui.QToolButton(self.soundBox)
        self.soundMetaBtn.setGeometry(QtCore.QRect(86, 40, 19, 19))
        self.soundMetaBtn.setStyleSheet(_fromUtf8("QToolButton {\n"
"\n"
"    border-image: url(:/new/infoBtn.png);\n"
"}"))
        self.soundMetaBtn.setObjectName(_fromUtf8("soundMetaBtn"))
        self.soundMetaBtn.clicked.connect(self.mediaInfo)
        self.addEgBtn = QtGui.QToolButton(self.soundBox)
        self.addEgBtn.setGeometry(QtCore.QRect(109, 42, 16, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.addEgBtn.setFont(font)
        self.addEgBtn.setAutoFillBackground(False)
        self.addEgBtn.setStyleSheet(_fromUtf8(""))
        self.addEgBtn.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.addEgBtn.setAutoRaise(True)
        self.addEgBtn.setObjectName(_fromUtf8("addEgBtn"))
        self.addEgBtn.clicked.connect(self.newMedia)
        self.delEgBtn = QtGui.QToolButton(self.soundBox)
        self.delEgBtn.setGeometry(QtCore.QRect(124, 42, 16, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.delEgBtn.setFont(font)
        self.delEgBtn.setStyleSheet(_fromUtf8(""))
        self.delEgBtn.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.delEgBtn.setAutoRaise(True)
        self.delEgBtn.setObjectName(_fromUtf8("delEgBtn"))
        self.delEgBtn.clicked.connect(self.delMedia)

        self.InnerBox = QtGui.QGroupBox(self.ButtonBox)
        self.InnerBox.setStyleSheet(_fromUtf8("QPushButton {\n"
                                              "\n min-width: 76px;"
                                              "\n min-height: 30px;"
                                              "\n max-width: 76px;"
                                              "\n max-height: 30px;\n}"))
        self.InnerBox.setGeometry(155,9,255,65)
        self.GridLayout = QtGui.QGridLayout(self.InnerBox)
        self.GridLayout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.GridLayout.setObjectName(_fromUtf8("ButtonLayout"))
        self.Del = QtGui.QPushButton()
        self.Del.setObjectName(_fromUtf8("Delete"))
        self.Del.clicked.connect(self.delRow)
        self.GridLayout.addWidget(self.Del,0,0)
        self.Clear = QtGui.QPushButton()
        self.Clear.setObjectName(_fromUtf8("Clear"))
        self.Clear.clicked.connect(self.clearAll)
        self.GridLayout.addWidget(self.Clear,1,0)
        self.Add = QtGui.QPushButton()
        self.Add.setObjectName(_fromUtf8("Add"))
        self.Add.clicked.connect(self.newRow)
        self.GridLayout.addWidget(self.Add,0,1)
        self.CancelBtn = QtGui.QPushButton()
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)       
        self.GridLayout.addWidget(self.CancelBtn,1,1)
        self.OkayBtn = QtGui.QPushButton()
        self.OkayBtn.setObjectName(_fromUtf8("OkayBtn"))
        self.OkayBtn.setDefault(1)
        self.GridLayout.addWidget(self.OkayBtn,1,2)
        self.OkayBtn.clicked.connect(self.OK)

        self.Del.setEnabled(0)
        self.Add.setEnabled(0)
        self.addEgBtn.setEnabled(0)
        self.delEgBtn.setEnabled(0)
        
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        if myapp.ui.dataIndex.unsavedEdit == 1:
            self.prevEdit = 1
        else:
            self.prevEdit = 0
        myapp.ui.dataIndex.unsavedEdit = 0

    def delRow(self):
        target = self.trackTable.whichTable
        target.removeRow(target.currentRow())
        myapp.ui.dataIndex.unsavedEdit = 1

    def newRow(self):
        target = self.trackTable.whichTable
        if QtCore.QObject.objectName(target) == 'grammar':
            column = 1
            prefixCell = QtGui.QTableWidgetItem(1002)
        elif QtCore.QObject.objectName(target) == 'C2':
            column = 0
        tableCell = QtGui.QTableWidgetItem(1002)
        tableCell.setText('new item')
        i = target.rowCount()
        target.insertRow(i)
        target.setItem(i,column,tableCell)
        if QtCore.QObject.objectName(target) == 'grammar':
            target.setItem(i,0,prefixCell)
        target.resizeRowToContents(i)
        myapp.ui.dataIndex.unsavedEdit = 1
            
    def setValues(self, currentCard):
        '''fills in the tables and fields with the initial values'''
        self.grammar.clear()
        self.C2.clear()
        node = myapp.ui.dataIndex.lexDict[currentCard]
        grmList = node.findall('Grm')
        C2List = node.findall('C2')
        CfList = node.findall('Cf')
        if len(grmList) != 0:
            self.grammar.setRowCount(0)
            for i in range(0,len(grmList)):
                try:
                    prefix = grmList[i].attrib.get('Prefix')
                except AttributeError:
                    prefix = None
                try:
                    mediaRef = grmList[i].attrib.get('MediaRef')
                except AttributeError:
                    mediaRef = None
                datum = grmList[i].text
                nextRow = self.grammar.rowCount()
                self.grammar.setRowCount(nextRow+1)
                newItem = QtGui.QTableWidgetItem(1001)
                if prefix != None:
                    newItem.setText(prefix)
                if mediaRef != None:
                    newItem.setData(35,mediaRef)
                newItem.setData(36,grmList[i])
                self.grammar.setItem(nextRow,0,newItem)
                nextItem = QtGui.QTableWidgetItem(1001)
                nextItem.setText(datum)
                self.grammar.setItem(nextRow,1,nextItem)
        else:
            newItem = QtGui.QTableWidgetItem(1001)
            self.grammar.setItem(0,0,newItem)
            nextItem = QtGui.QTableWidgetItem(1001)
            nextItem.setText('new Item')
            self.grammar.setItem(0,1,nextItem)
            self.grammar.setRowCount(1)
        if len(C2List) != 0:
            self.C2.setRowCount(0)
            for i in range(0,len(C2List)):
                try:
                    mediaRef = C2List[i].attrib.get('MediaRef')
                except AttributeError:
                    mediaRef = None
                datum = C2List[i].text
                nextRow = self.C2.rowCount()
                self.C2.setRowCount(nextRow+1)
                newItem = QtGui.QTableWidgetItem(1001)
                if mediaRef != None:
                    newItem.setData(35,mediaRef)
                newItem.setData(36,C2List[i])
                newItem.setText(datum)
                self.C2.setItem(nextRow,0,newItem)
        else:
            nextItem = QtGui.QTableWidgetItem(1001)
            nextItem.setText('new Item')
            self.C2.setItem(0,0,nextItem)
            self.C2.setRowCount(1)              
        if len(CfList) != 0:
            textLine = ''
            for item in CfList:
                CfLine = item.text
                if len(textLine) == 0:
                    textLine = CfLine
                else:
                    textLine += ',' + CfLine
            self.cf.setText(textLine)

    def selectElement(self, target):
        '''responds to user click on table'''
        gManager.addEgBtn.setEnabled(1)
        gManager.delEgBtn.setEnabled(0)
        gManager.Del.setEnabled(1)
        gManager.Add.setEnabled(1)
        gManager.recordings.clear()
        gManager.soundFileMeta.clear()
        if QtCore.QObject.objectName(target) == 'C2':
            column = 0
        elif QtCore.QObject.objectName(target) == 'grammar':
            column = 1
        else:
            return
        if target.item(target.currentRow(),column) == None:
            tableCell = QtGui.QTableWidgetItem(1002)
            target.setItem(target.currentRow(),column,tableCell)                
        howMany = 1
        for i in range(0,target.rowCount()):
            if target.item(i,column):
                howMany += 1
        try:
            if target.item(target.currentRow(),0).data(35):
                gManager.delEgBtn.setEnabled(1)
                gManager.addEgBtn.setEnabled(0)
                MediaRef = target.item(target.currentRow(),0).data(35)
                gManager.recordings.clear()
                gManager.soundFileMeta.clear()
                mediaElement = myapp.ui.dataIndex.mediaDict[MediaRef]
                recording = mediaElement.attrib.get('Filename')
                speaker = mediaElement.attrib.get('Spkr')
                date = mediaElement.attrib.get('Date')
                gManager.recordings.insertItem(0,recording)
                gManager.recordings.setItemData(0,MediaRef,35)
                gManager.recordings.setCurrentIndex(0)
                gManager.soundFileMeta.setText(speaker + " " + date)
        except AttributeError:
            pass
        target.editItem(target.currentItem())
        
    def mediaInfo(self):
        mediaNode = gManager.recordings.itemData(0,35)
        mManager = MediaManager()
        mManager.renameWindow(gManager.recordings.currentText())
        mManager.setValues(mediaNode)
        if myapp.ui.dataIndex.unsavedEdit == 1:
            toggleUE = 1
            myapp.ui.dataIndex.unsavedEdit = 0
        else:
            toggleUE = None
        if mManager.exec_() and myapp.ui.dataIndex.unsavedEdit == 1:
            metaData = mManager.getValues()
            for child in myapp.ui.dataIndex.root.iter('Media'):
                if child.attrib.get('MedID') == mediaNode:
                    if len(metaData[0]) != 0:
                        child.set('Spkr',metaData[0])
                    if len(metaData[1]) != 0:
                        child.set('Rschr',metaData[1])
                    if len(metaData[2]) != 0:
                        child.set('Date',metaData[2])
                    if len(metaData[3]) != 0:
                        child.set('Apparatus',metaData[3])
                    if len(metaData[4]) != 0:
                        child.set('Catalog',metaData[4])
                    if len(metaData[5]) != 0:
                        if child.find('Comments') == None:
                            etree.SubElement(child,'Comments')
                            child[0].text = metaData[5]
                        else:
                            child.find('Comments').text = metaData[5]
                    if len(metaData[6]) != 0:
                        child.set('FileType',metaData[6])
                    gManager.soundFileMeta.setText(metaData[0] + " " + metaData[2])
                    break
        if toggleUE != None:
            myapp.ui.dataIndex.unsavedEdit = 1               

    def playSound(self):
        caller = self.recordings
        btnCmds.playSound(caller)

    def newMedia(self):
        caller = self.recordings
        mdField = 'gManager'
        table = gManager.trackTable.whichTable
        newNode = btnCmds.newMedia(caller,mdField)
        medID = newNode.attrib.get('MedID')
        try:
            speaker = newNode.attrib.get('Spkr')
        except AttributeError:
            speaker = ''
        try:
            date = newNode.attrib.get('Date')
        except AttributeError:
            date = ''
        self.soundFileMeta.setText(speaker + ' ' + date)
        r = self.grammar.currentRow()
        c = self.C2.currentRow()
        if table == 'grammar':
            self.grammar.item(r,0).setData(35,medID)
            for child in myapp.ui.dataIndex.root.iter('Lex'):
                if child.attrib.get('LexID') == myapp.ui.dataIndex.currentCard:
                    gNode = self.grammar.item(r,0).data(36)
                    gNode.set('MediaRef',medID)
                    break
        elif table == 'C2':
            self.C2.item(c,0).setData(35,medID)
            for child in myapp.ui.dataIndex.root.iter('Lex'):
                if child.attrib.get('LexID') == myapp.ui.dataIndex.currentCard:
                    gNode = self.C2.item(r,0).data(36)
                    gNode.set('MediaRef',medID)
                    break
        self.addEgBtn.setEnabled(0)
        self.delEgBtn.setEnabled(1)
            
    def delMedia(self):
        self.soundFileMeta.clear()
        caller = self.recordings
        medID = caller.itemData(caller.currentIndex(),35)
        mdField = 'gManager'
        table = gManager.trackTable.whichTable
        lexNode = btnCmds.delMedia(caller,mdField)
        if lexNode.find('Grm[@MediaRef="%s"]'%medID) != None:
            badNode = lexNode.find('Grm[@MediaRef="%s"]'%medID)
            del badNode.attrib['MediaRef']
        if lexNode.find('C2[@MediaRef="%s"]'%medID) != None:
            badNode = lexNode.find('C2[@MediaRef="%s"]'%medID)
            del badNode.attrib['MediaRef']
        if table == 'grammar':
            i = self.grammar.currentRow()
            self.grammar.item(i,0).setData(35,None)
        elif table == 'C2':
            i = self.C2.currentRow()
            self.C2.item(i,0).setData(35,None)        
        self.recordings.clear()             
        myapp.ui.dataIndex.unsavedEdits = 1
        self.addEgBtn.setEnabled(1)
        self.delEgBtn.setEnabled(0)
        myapp.ui.dataIndex.lexDict[myapp.ui.dataIndex.currentCard] = lexNode

    def cancelled(self,checked):
        if self.prevEdit == 0:
            myapp.ui.dataIndex.unsavedEdit = 0
        else:
            myapp.ui.dataIndex.unsavedEdit = 1
        self.reject()

    def updateXML(self):
        '''updates XML and grammar field on lex card'''
        self.grammar.sortItems(1,0)
        self.grammar.sortItems(0,0)
        fieldContents = ''
        for child in myapp.ui.dataIndex.root.iter('Lex'):
            if child.attrib.get('LexID') == myapp.ui.dataIndex.currentCard:
                killList = []
                for node in child.iter('Grm'):
                    killList.append(node)
                for item in killList:
                    child.remove(item)
                killList = []
                for node in child.iter('C2'):
                    killList.append(node)
                for item in killList:
                    child.remove(item)
                killList = []
                for node in child.iter('Cf'):
                    killList.append(node)
                for item in killList:
                    child.remove(item)
                index = 3
                refList = []
                altList = []
                for i in range(0,self.grammar.rowCount()):
                    if self.grammar.item(i,0) == None:
                        break
                    newGrm = etree.Element('Grm')
                    newGrm.text = self.grammar.item(i,1).text()
                    if len(self.grammar.item(i,0).text()) != 0:
                        newGrm.set("Prefix",self.grammar.item(i,0).text())
                        fieldContents += "<i>" + self.grammar.item(i,0).text() + ".</i> "
                    if self.grammar.item(i,0).data(35) != None:
                        newGrm.set("MediaRef",self.grammar.item(i,0).data(35))
                        refList.append(self.grammar.item(i,0).data(35))
                        altList.append(self.grammar.item(i,1).text())
                    child.insert(index,newGrm)
                    fieldContents += newGrm.text
                    if i < self.grammar.rowCount()-1:
                        fieldContents += "<br/>"
                    index += 1
                for i in range(0,self.C2.rowCount()):
                    if self.C2.item(i,0) == None:
                        break
                    newC2 = etree.Element('C2')
                    newC2.text = self.C2.item(i,0).text()
                    if self.C2.item(i,0).data(35) != None:
                        newC2.set("MediaRef",self.C2.item(i,0).data(35))
                        refList.append(self.C2.item(i,0).data(35))
                        altList.append(self.C2.item(i,0).text())
                    child.insert(index,newC2)
                    if len(fieldContents) == 0:
                        fieldContents = "<i>also</i> "
                        fieldContents += newC2.text
                    elif i == 0:
                        fieldContents += "<br/>"
                        fieldContents += "<i>also</i> "
                        fieldContents += newC2.text                        
                    elif i < self.C2.rowCount():
                        fieldContents += ", "
                        fieldContents += newC2.text
                    else:
                        fieldContents += newC2.text
                    index += 1
                if len(self.cf.toPlainText()) != 0:
                    CfInfo = self.cf.toPlainText()
                    CfElems = CfInfo.split(', ')
                    j = 1
                    for item in CfElems:
                        newCross = etree.Element('Cf')
                        newCross.text = item
                        crossRef = None
                        for entry in myapp.ui.dataIndex.root.findall('Lex'):
                            lexeme = entry.find('Orth').text
                            if lexeme == item and entry.attrib.get('Hom') != None:
                                synList = entry.attrib.get('Hom').split(", ")
                                synList.append(entry.attrib.get('LexID'))
                                newCf = crossRefManager()
                                newCf.setRefs(synList)
                                if newCf.exec_():
                                    crossRef = newCf.getRef()
                                else:
                                    crossRef = None
                                break
                            elif lexeme == item:
                                crossRef = entry.attrib.get('LexID')
                                break
                        if crossRef != None:
                            newCross.set("CrossRef",crossRef)
                            refList.append(crossRef)
                            altList.append(item)
                        child.insert(index,newCross)
                        index += 1

                        if len(fieldContents) == 0:
                            fieldContents = "<i>cf.</i> "
                        else:
                            if j == 1:
                                fieldContents += "<br/><i>cf.</i> "
                                j += 1
                            else:
                                fieldContents += ", "
                        if crossRef == None:
                            fieldContents += '<span style="color:red">' + item + "</span>"
                        else:
                            fieldContents += item

                if len(refList) != 0:
                    field = 'lGrammar'
                    cardLoader.buildContextMenu(field,refList,altList)
                else:
                    try:
                        del(myapp.ui.lGrammar.crossrefMenu)
                    except AttributeError:
                        pass
                myapp.ui.lGrammar.clear()
                myapp.ui.lGrammar.insertHtml(fieldContents)
                break

    def OK(self,checked):
        node = myapp.ui.dataIndex.lexDict[myapp.ui.dataIndex.currentCard]
        if myapp.ui.dataIndex.unsavedEdit == 1:
            self.updateXML()
        if self.prevEdit == 1:
            myapp.ui.dataIndex.unsavedEdit = 1
        node = myapp.ui.dataIndex.lexDict[myapp.ui.dataIndex.currentCard]
        self.accept()
                
    def clearAll(self):
        self.C2.clear()
        self.cf.clear()
        self.grammar.clear()
        self.Del.setEnabled(0)
        self.Add.setEnabled(1)
        self.addEgBtn.setEnabled(0)
        self.delEgBtn.setEnabled(0)
        self.recordings.clear()
        self.soundFileMeta.clear()
              
    def retranslateUi(self, GrammarManager):
        GrammarManager.setWindowTitle(QtGui.QApplication.translate("GrammarManager", "Grammar and cross-references", None, QtGui.QApplication.UnicodeUTF8))
        self.Clear.setText(QtGui.QApplication.translate("GrammarManager", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.Clear.setToolTip(QtGui.QApplication.translate("GrammarManager", "clear all fields", None, QtGui.QApplication.UnicodeUTF8))
        self.Del.setText(QtGui.QApplication.translate("GrammarManager", "Del", None, QtGui.QApplication.UnicodeUTF8))
        self.Del.setToolTip(QtGui.QApplication.translate("GrammarManager", "delete selection", None, QtGui.QApplication.UnicodeUTF8))
        self.Add.setText(QtGui.QApplication.translate("GrammarManager", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.Add.setToolTip(QtGui.QApplication.translate("GrammarManager", "add new grammatical information\n or alternative form (select field to edit)", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("GrammarManager", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setToolTip(QtGui.QApplication.translate("GrammarManager", "close window without saving", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setText(QtGui.QApplication.translate("GrammarManager", "Okay", None, QtGui.QApplication.UnicodeUTF8))
        self.OkayBtn.setToolTip(QtGui.QApplication.translate("GrammarManager", "close window and save changes", None, QtGui.QApplication.UnicodeUTF8))
        self.grammarLabel.setText(QtGui.QApplication.translate("GrammarManager", "Grammatical information:", None, QtGui.QApplication.UnicodeUTF8))
        self.grammar.setToolTip(QtGui.QApplication.translate("GrammarManager", "grammatical information, abbreviations for grammatical \n"
                                                             "categories can be placed in the first column on the left", None, QtGui.QApplication.UnicodeUTF8))
        self.C2Label.setText(QtGui.QApplication.translate("GrammarManager", "Alternative forms:", None, QtGui.QApplication.UnicodeUTF8))
        self.C2.setToolTip(QtGui.QApplication.translate("GrammarManager", "alternative forms not in dictionary", None, QtGui.QApplication.UnicodeUTF8))
        self.cfLabel.setText(QtGui.QApplication.translate("GrammarManager", "Cross-references:", None, QtGui.QApplication.UnicodeUTF8))
        self.cf.setToolTip(QtGui.QApplication.translate("GrammarManager", "other related entries", None, QtGui.QApplication.UnicodeUTF8))
        self.recordings.setToolTip(QtGui.QApplication.translate("GrammarManager", "recordings", None, QtGui.QApplication.UnicodeUTF8))
        self.playSoundBtn.setToolTip(QtGui.QApplication.translate("GrammarManager", "play recording", None, QtGui.QApplication.UnicodeUTF8))
        self.soundFileMeta.setToolTip(QtGui.QApplication.translate("GrammarManager", "speaker info for recording", None, QtGui.QApplication.UnicodeUTF8))
        self.soundMetaBtn.setToolTip(QtGui.QApplication.translate("GrammarManager", "metadata", None, QtGui.QApplication.UnicodeUTF8))
        self.addEgBtn.setToolTip(QtGui.QApplication.translate("GrammarManager", "add media file", None, QtGui.QApplication.UnicodeUTF8))
        self.addEgBtn.setText(QtGui.QApplication.translate("GrammarManager", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.delEgBtn.setToolTip(QtGui.QApplication.translate("GrammarManager", "delete media file", None, QtGui.QApplication.UnicodeUTF8))
        self.delEgBtn.setText(QtGui.QApplication.translate("GrammarManager", "-", None, QtGui.QApplication.UnicodeUTF8))

        ##### END GrammarManager####
        
class DrvnManager(QtGui.QDialog):
    '''class for selecting lexical entries to link to'''
    def __init__(self, parent=None):
        super(DrvnManager,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.setObjectName(_fromUtf8("DrvnManager"))
        self.resize(300, 471)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)
        self.setStyleSheet("QGroupBox {\n margins: 0px;\n}\n QPushButton {\n"
                                              "\n min-width: 76px;"
                                              "\n min-height: 30px;"
                                              "\n max-width: 76px;"
                                              "\n max-height: 30px;\n}")
        
        self.lexBox = QtGui.QGroupBox(self)
        self.lexBox.setGeometry(QtCore.QRect(10, 9, 280, 400))
        self.lexBox.setObjectName(_fromUtf8("lexBox"))
        self.lexList = QtGui.QListWidget(self.lexBox)
        self.lexList.setGeometry(3,3,274,394)
        self.lexList.itemClicked.connect(self.setData)
        self.lexList.setAlternatingRowColors(True)
        self.lexList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.lexList.itemDoubleClicked.connect(self.setDataAndGo)

        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 415, 280, 56))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonBox.sizePolicy().hasHeightForWidth())
        self.ButtonBox.setSizePolicy(sizePolicy)
        self.ButtonBox.setTitle(_fromUtf8(""))
        self.ButtonBox.setFlat(True)
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ButtonBox)
        self.horizontalLayout.setObjectName(_fromUtf8("ButtonLayout"))
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.CancelBtn = QtGui.QPushButton(self.ButtonBox)
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)       
        self.horizontalLayout.addWidget(self.CancelBtn)
        self.OkayBtn = QtGui.QPushButton(self.ButtonBox)
        self.OkayBtn.setObjectName(_fromUtf8("OkayBtn"))
        self.OkayBtn.setDefault(1)
        self.horizontalLayout.addWidget(self.OkayBtn)
        self.OkayBtn.clicked.connect(self.okay)
        
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def listEntries(self):
        for child in myapp.ui.dataIndex.root.iter('Lex'):
            derID = child.attrib.get('LexID')
            lexeme = child.findtext('Orth')
            POS = child.findtext('POS')
            L1 = child.findtext('Def/L1')
            try:
                text = lexeme + " (" + POS + ") " + L1
            except TypeError:
                text = lexeme + " " + L1
            item = QtGui.QListWidgetItem()
            item.setData(32, derID)
            item.setText(text)
            self.lexList.addItem(item)        
        self.setWindowTitle(QtGui.QApplication.translate("DrvnManager", "Select lexical entry", None, QtGui.QApplication.UnicodeUTF8))

    def listDerivatives(self):
        self.lexList.clear()
        for i in range(0,myapp.ui.lDerivatives.count()):
            derID = myapp.ui.lDerivatives.item(i).data(32)
            text = myapp.ui.lDerivatives.item(i).text()
            item = QtGui.QListWidgetItem()
            item.setData(32, derID)
            item.setText(text)
            self.lexList.addItem(item)           
        self.setWindowTitle(QtGui.QApplication.translate("DrvnManager", "Remove derivation", None, QtGui.QApplication.UnicodeUTF8))

    def setDataAndGo(self):
        self.setData()
        self.accept()

    def setData(self):
        data = self.lexList.currentItem().data(32)
        return(data)

    def okay(self):
        self.accept()

    def cancelled(self,checked):
        self.reject()

    def retranslateUi(self, DrvnManager):
        self.OkayBtn.setText(QtGui.QApplication.translate("DrvnManager", "Okay", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("DrvnManager", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.lexList.setToolTip(QtGui.QApplication.translate("DrvnManager", "select entry to link to", None, QtGui.QApplication.UnicodeUTF8))


class EntryManager(QtGui.QDialog):
    '''class for selecting lexical entries to link to'''
    def __init__(self, parent=None):
        super(EntryManager,self).__init__(parent=None)
        QtGui.QDialog.__init__(self,parent)
        try:
            _fromUtf8 = QtCore.QString.fromUtf8
        except AttributeError:
            _fromUtf8 = lambda s: s

        self.setObjectName(_fromUtf8("EntryManager"))
        self.resize(400, 471)
        self.setAutoFillBackground(True)
        self.setSizeGripEnabled(False)
        self.setStyleSheet("QGroupBox {\n margins: 0px;\n}\n QPushButton {\n"
                                              "\n min-width: 76px;"
                                              "\n min-height: 30px;"
                                              "\n max-width: 76px;"
                                              "\n max-height: 30px;\n}")
        
        self.lexBox = QtGui.QGroupBox(self)
        self.lexBox.setGeometry(QtCore.QRect(10, 9, 380, 400))
        self.lexBox.setObjectName(_fromUtf8("lexBox"))
        self.lexList = QtGui.QTreeWidget(self.lexBox)
        self.lexList.setColumnCount(1)
        self.lexList.setGeometry(3,3,374,394)
        self.lexList.header().hide()
        self.lexList.itemClicked.connect(self.setData)
        self.lexList.setAlternatingRowColors(True)
        self.lexList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.lexList.itemDoubleClicked.connect(self.setDataAndGo)
        delegate = HTMLDelegate()
        self.lexList.setItemDelegate(delegate)
        
        self.ButtonBox = QtGui.QGroupBox(self)
        self.ButtonBox.setGeometry(QtCore.QRect(9, 415, 380, 56))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ButtonBox.sizePolicy().hasHeightForWidth())
        self.ButtonBox.setSizePolicy(sizePolicy)
        self.ButtonBox.setTitle(_fromUtf8(""))
        self.ButtonBox.setFlat(True)
        self.ButtonBox.setObjectName(_fromUtf8("ButtonBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.ButtonBox)
        self.horizontalLayout.setObjectName(_fromUtf8("ButtonLayout"))
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.CancelBtn = QtGui.QPushButton(self.ButtonBox)
        self.CancelBtn.setObjectName(_fromUtf8("CancelBtn"))
        self.CancelBtn.clicked.connect(self.cancelled)       
        self.horizontalLayout.addWidget(self.CancelBtn)
        self.OkayBtn = QtGui.QPushButton(self.ButtonBox)
        self.OkayBtn.setObjectName(_fromUtf8("OkayBtn"))
        self.OkayBtn.setDefault(1)
        self.horizontalLayout.addWidget(self.OkayBtn)
        self.OkayBtn.clicked.connect(self.okay)
        
        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def listEntries(self):
        for child in myapp.ui.dataIndex.root.iter('Lex'):
            derID = child.attrib.get('LexID')
            lexeme = child.findtext('Orth')
            POS = child.findtext('POS')
            L1List = child.findall('Def/L1')
            item = QtGui.QTreeWidgetItem()
            item.setData(0,32,derID)
            for i in range(0,len(L1List)):
                L1 = L1List[i].text
                L1 = L1.replace('{Italics}','<i>')
                L1 = L1.replace('{/Italics}','</i>')
                L1 = L1.replace('{{','<')
                L1 = L1.replace('}}','>')
                L1 = L1.replace('{','<')
                L1 = L1.replace('}','>')
                if len(L1List) != 1:
                    indexNo = str(i+1) + ") "
                else:
                    indexNo= None
                if indexNo == None:
                    try:
                        txt1 = lexeme + " (" + POS + ") " + L1
                    except TypeError:
                        txt1 = lexeme + " " + L1                           
                    item.setText(0,txt1)
                    item.setData(0,33,1)
                else:
                    if i ==0:
                        try:
                            txt1 = lexeme + " (" + POS + ") "
                        except TypeError:
                            txt1 = lexeme + " "                           
                        item.setText(0,txt1)
                        item.setData(0,33,i+1)
                    txt = indexNo + L1
                    defItem = QtGui.QTreeWidgetItem(item)
                    defItem.setText(0,txt)
                    defItem.setData(0,32,derID)
                    defItem.setData(0,33,i+1)
            self.lexList.addTopLevelItem(item)
            item.setExpanded(1)
        self.setWindowTitle(QtGui.QApplication.translate("EntryManager", "Select lexical entry", None, QtGui.QApplication.UnicodeUTF8))

    def setDataAndGo(self):
        self.setData()
        self.accept()

    def setData(self):
        entry = self.lexList.currentItem().data(0,32)            
        index = self.lexList.currentItem().data(0,33)
        data = [entry, index]
        return(data)

    def okay(self):
        self.accept()

    def cancelled(self,checked):
        self.reject()

    def retranslateUi(self, EntryManager):
        self.OkayBtn.setText(QtGui.QApplication.translate("EntryManager", "Okay", None, QtGui.QApplication.UnicodeUTF8))
        self.CancelBtn.setText(QtGui.QApplication.translate("EntryManager", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.lexList.setToolTip(QtGui.QApplication.translate("EntryManager", "select entry to link to", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  QtCore.QCoreApplication.setOrganizationName("UNT Project")
  QtCore.QCoreApplication.setApplicationName("Electronic Fieldbook")
  QtCore.QCoreApplication.setOrganizationDomain("www.arts.ualberta.ca/~totonaco")
  global myapp
  myapp = Fieldbook()
  myapp.show()
  sys.exit(app.exec_())

