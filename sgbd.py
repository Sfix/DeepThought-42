# Management of the database

import pandas as pd
import numpy as np

actionOnePlus  = '👍'
actionOneMinus = '👎'

def actionOppose(action):
    if action == actionOnePlus:
        return actionOneMinus
    if action == actionOneMinus:
        return actionOnePlus

# Name of the database
defaultDBName = "GR2HS"
info = ['tStamp', 'chatId', 'userId', 'msgId', 'action', 'content']

class DB():
    """
    Manage the database of approuval and disapprouval.
    

    Returns:
        [type] -- [description]
    """
    nomDB = "Non renseigné"
    df = pd.DataFrame([], columns=info)

    def __init__(self, nomDB=defaultDBName):
        self.nomDB = nomDB
        self.df = pd.DataFrame([], columns=info)
        print("table créé")

    def alreadyPlusOne(self, marcheur, msg):
        # What is memorized is the original message
        msg = msg.reply_to_message
        results = self.df[(self.df['userId'] == marcheur.id)                  \
                            & (self.df['msgId'] == msg.message_id)]
        if not results.empty:
            results = results[results[info[4]] == actionOnePlus]
        return not results.empty

    def alreadyMinusOne(self, marcheur, msg):
        # What is memorized is the original message
        results = self.df[(self.df['userId'] == marcheur.id)                  
                            & (self.df['msgId'] 
                                    == msg.reply_to_message.message_id)]
        if not results.empty:
            results = results[results[info[4]] == actionOneMinus]
        return not results.empty

    def createEntry(self,
                    date   = np.nan,                                              
                    chatId = np.nan,                                              
                    userId = np.nan,                                              
                    msgId  = np.nan,
                    action = np.nan,
                    content= np.nan):
        # Doit faire le test des valeurs fondamentales
        return {
                    info[0] : date,
                    info[1] : chatId,
                    info[2] : userId,
                    info[3] : msgId,
                    info[4] : action,
                    info[5] : content
               }


    def add(self, msg, action):
        # check if it is not already voted
        if not self.df.empty:
            rdf = self.df[self.df[info[1]] == msg.chat_id]
            rrdf = rdf[rdf[info[2]] == msg.from_user.id]
            rrrdf = rrdf[rrdf[info[3]] == msg.reply_to_message.message_id]
            if not rrrdf.empty:
                opposeAction = actionOppose(action) 
                row = rrrdf[rrrdf[info[4]] == opposeAction] 
                if row.empty:
                    msg = "Vous aviez déjà voté {0} pour ce message.".format(action)
                    return msg
                else:
                    msg = "Vous aviez déjà voté {0} pour ce message,".format(opposeAction)           \
                            + " j'annule ce vote précédent."
                    self.df = self.df.drop(row.index)
                    return msg
        self.df = self.df.append(self.createEntry(
                                            msg.date,
                                            msg.chat_id,
                                            msg.from_user.id,
                                            msg.reply_to_message.message_id,
                                            action,
                                            msg.reply_to_message.text),
                                 ignore_index = True)
        return ""

    def remove(self, chatId, userId, replyMsgId, action):
        # Checl if not already empty
        if self.df.empty:
            return
        # check if it is not already voted
        row = self.df[(self.df[info[1]] == chatId)                            \
                        and (self.df[info[2]] == userId)                      \
                        and (self.df[info[3]] == replyMsgId)                  \
                        and (self.df[info[4]] == action)]
        if not row.empty:
            self.df = self.df.drop(row.index)
            self.df.reset_index(drop=True)

    def msgEtat(self, chatId):
        dfs = self.df[self.df[info[1]] == chatId]
        msg = ""
        while not dfs.empty:
            firstRow = dfs.head(1)
            index = firstRow.index[0]
            curMsgId = firstRow[info[3]][index]
            curMsg   = firstRow[info[5]][index]
            msg = msg + '<b>Message:</b> "{0}"\n'.format(curMsg)
            subDF = dfs[dfs[info[3]] == curMsgId]
            subDFP1 = subDF[subDF[info[4]] == actionOnePlus]
            subDFM1 = subDF[subDF[info[4]] == actionOneMinus]
            msg = msg +                                                       \
                    "à #{0}\n{1} {2} et {3} {4} pour total {5}".format(
                            curMsgId,
                            len(subDFP1),
                            actionOnePlus,
                            len(subDFM1),
                            actionOneMinus,
                            len(subDFP1) - len(subDFM1)
                        )
            dfs = dfs[dfs[info[3]] != curMsgId]
            if not dfs.empty:
                msg = msg  + "\n"
        if msg == "":
            msg = "Aucun message plébicité ou critiqué pour l'instant"
        return msg

