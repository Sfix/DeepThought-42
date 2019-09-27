# 
#? L'API des bot est ici https://core.telegram.org/bots/api
#

from sgbd import DB
from sgbd import actionOnePlus, actionOneMinus


class Robot():
    """
    Classe portant le bot avec les variables importantes
    pour le fonctionnement.
    """

    ordreStart = ['start', 'run', 'go']
    ordreStop = ['stop']
    ordreStat = ['stat']
    ordrePlusOne = ['/+1', '+1',
                   '/👍', '/👍🏻', '/👍🏼', '/👍🏽', '/👍🏾', '/👍🏿',
                   '/👌', '/👌🏻', '/👌🏼', '/👌🏽', '/👌🏾', '/👌🏿',
                   '👍', '👍🏻', '👍🏼', '👍🏽', '👍🏾', '👍🏿',
                   '👌', '👌🏻', '👌🏼', '👌🏽', '👌🏾', '👌🏿'] 
    ordreMinusOne = ['/-1', '-1',
                    '/👎', '/👎🏻', '/👎🏼', '/👎🏼', '/👎🏾', '/👎🏿',
                    '👎', '👎🏻', '👎🏼', '👎🏼', '👎🏾', '👎🏿']
 

    msg = "Pas encore initialisé"
    msgStatusId = -1

    def __init__(self):
        self.dbPlusMoins = DB("sgbdP1M1")
        return

    def isRunning(self):
        return self.msgStatusId > 0

    def start(self, update, context):
        """Lancement du robot.

        Nous testons si le robot est déjà lancé grâce à msgStatusId.
        Dans le cas positif nous avertissons que cela est le cas
        # TODO effacer le message et écrire le pourquoi à celui qui envois
        Dans le cas négatif nous lançons le message de status après avoir
        informé de la création
        # TODO mettre le message status en Pin
        
        Arguments:
            update {telegram.ext.Updater} -- Updater du bot 
            context {telegram.ext.callbackcontext.callbackcontext} -- Contect du bot
        """
        # Test si c'est la première fois que la commande est reçue grâce 
        # à l'ID du message de status.
        if self.isRunning():
            # TODO : créer un retour plus adapté.
            msg = "Je suis déjà réveillé."  
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=msg,
                                     parse_mode='HTML')
            return
        # A ce point, c'est la première fois que la commande est reçue
        # il faut démarer le robot.
        msg =                                                                 \
            "<strong>Bonjour !</strong>\n" +                                          \
            "Merci de m'avoir réveillé. Je crée tout ce qu'il faut pour " + \
            "aider la gestion de cette boucle."  
        context.bot.send_message(chat_id=update.message.chat_id,
                                    text=msg,
                                    parse_mode='HTML')
        msg =                                                                 \
            "<strong>État de la boucle</strong>\n<b>Base des données</b>\n" + \
            self.dbPlusMoins.msgEtat(update.message.chat_id)
        context.bot.send_message(chat_id=update.message.chat_id,
                                    text=msg,
                                    parse_mode='HTML')
        # Nous utilisons ce message pour faire le compte rendu du robot
        self.msgStatusId = update.message.message_id + 2
        # TODO : pin this message


    def stop(self, update, context):
        """Gère la réception d'une demande d'arrêt du robot.

        Le robot ne peut pas s'arrêter. Il reste en permanence en fonctionnement.
        Un message est donc envoyé pour le signaler

        # TODO : Faire un envois en message privé et suprimer le message envoyant.
        
        Arguments:
            update {telegram.ext.Updater} -- Updater du bot 
            context {telegram.ext.callbackcontext.callbackcontext} -- Contect du bot
        """
        # TODO : Faire le cas du robot non lancé.
        msg =                                                                 \
            "Une fois lancé, je continue ma fonction sans faiblir."
        context.bot.send_message(chat_id=update.message.chat_id,
                                    text=msg,
                                    parse_mode='HTML')

    def stat(self, update, context):
        msg =                                                                 \
            "<strong>État de la boucle</strong>\n<b>Base des données</b>\n"   \
            + self.dbPlusMoins.msgEtat(update.message.chat_id) + "\n"         \
            + "\nVous avez aussi accés dans le message épinglé"
        # TODO : Trouver une solution pour avoir un lien plutôt qu'un Reply
        context.bot.send_message(chat_id=update.message.chat_id,
                                    text=msg,
                                    parse_mode='HTML',
                                    reply_to_message_id=self.msgStatusId)


    def text(self, update, context):
        # Le test du reveille se fait dans la fonction
        if (update.message.text in self.ordrePlusOne):
            self.reactSurMessage(update, context, 
                                    self.dbPlusMoins.add, actionOnePlus)
            return
        if (update.message.text in self.ordreMinusOne):
            self.reactSurMessage(update, context, 
                                    self.dbPlusMoins.add, actionOneMinus)
            return


    def reactSurMessage(self, update, context, traitement, action):
        if not self.isRunning():
            # TODO : créer un retour plus adapté.
            msg = "Veuillez me réveiller ('/start') avant de donner ." +      \
                "un {0} à un message".format(update.message.text)  
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text=msg,
                                     parse_mode='HTML')
            return
        if update.message.reply_to_message is None:
            # TODO : créer un meilleur retour
            msg = "Pour approuver un message, veuillez faire un 'Reply'"      \
                    + " dessus et mettez le '{s}' ".format(s=update.message.text)    \
                    + "dans le corps du message."
            context.bot.send_message(chat_id=update.message.chat_id,          
                                        text=msg,
                                        parse_mode='HTML')
            return
        # TODO : gérer le cas ou le message est un reply à un message. Il faut 
        # TODO : demander à l'expéditeur s'il est pour le message d'origine ou
        # TODO : pour la réponse qui lui est faite.
        msg = traitement(update.message, action)
        # Nous utilisons ce message pour faire le compte rendu du robot
        if len(msg) > 0:
            context.bot.send_message(chat_id=update.message.chat_id,          
                                            text=msg,
                                            parse_mode='HTML')
        # On affiche le résultat car cela peut avoir été une annulation de vote
        msg =                                                                 \
            "<strong>État de la boucle</strong>\n<b>Base des données</b>\n"   \
            + self.dbPlusMoins.msgEtat(update.message.chat_id)
        context.bot.edit_message_text(chat_id=update.message.chat_id,
                                            text=msg,
                                            parse_mode='HTML',
                                            message_id=self.msgStatusId)



