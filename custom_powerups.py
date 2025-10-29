# ba_meta require api 9

"""
    Custom Powerups by EmperorR(NULL)
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import babase
import bauiv1 as bui
import bascenev1 as bs
import bascenev1lib
from random import choice, random, randrange
from bascenev1lib.actor.bomb import (Blast,
       ExplodeMessage, ArmMessage, BombFactory,
       WarnMessage, ImpactMessage, ExplodeHitMessage,
       )
from bascenev1lib.actor.popuptext import PopupText
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import NoReturn, Sequence, Any, Callable 

def get_custom_powerups() -> dict[str, int]:
    """ custom powerups """
    powerups = {
       'random': 2,
       'fake': 2,
       'ice_impact_bombs': 0,
       'ice_mines': 0,
       'invisible': 2,
    }
    return powerups

# ba_meta export plugin
class Plugin(babase.Plugin): 
     
    # Here we use the decorators to add extra code in original fuction
    def pbx_factory_new_init(func):
        def wrapper(*args):
            # Original code.
            func(*args)
            
            custom_powerups: dict[str, int] = get_custom_powerups()
            
            # in original code all power randomly picked up from self._powerupdist list attribute
            # so we just need to add our custom power in "self._powerupdist" list
            for powerup in custom_powerups:
                 for _ in range(int(custom_powerups[powerup])):
                     args[0]._powerupdist.append(powerup)
            
        return wrapper
    
    # replace orignal one to custom one
    bascenev1lib.actor.powerupbox.PowerupBoxFactory.__init__ = pbx_factory_new_init(bascenev1lib.actor.powerupbox.PowerupBoxFactory.__init__)
    
    # Here we make our boxes for our custom powerups.
    # With help of decorators.
    def pbx_new_init(func):
        def wrapper(*args, **kwargs):
            
            new_powerup: str | None = None
            # Checking if poweruptype is a custom to avoid error from original code
            # Need to check that because for original code our powerup is invalid 
            if kwargs['poweruptype'] in get_custom_powerups():
                
                new_powerup = kwargs['poweruptype']
                # Changing the value of custom to default to avoid error from else statement in original code
                kwargs['poweruptype'] = 'triple_bombs'
            
            # Orignal code
            # this orignal code create box for as 
            func(*args, **kwargs)
            
            if new_powerup is not None:
                # Replace default to custom 
                args[0].poweruptype  =  new_powerup
               
                # texturing default powerupbox to custom
                if args[0].poweruptype == 'random':
                    args[0].node.color_texture = bs.gettexture('achievementEmpty')
                    
                elif args[0].poweruptype == 'ice_impact_bombs':
                    args[0].node.color_texture = bs.gettexture('bombColorIce')
                
                elif args[0].poweruptype == 'ice_mines':
                    args[0].node.color_texture = bs.gettexture('achievementMine')
                    
                elif args[0].poweruptype == 'invisible':
                    args[0].node.color_texture = bs.gettexture('empty')
                    
                elif args[0].poweruptype == 'fake':
                    fake_tex = (
                        'powerupBomb',
                        'powerupPunch',
                        'powerupShield',
                        'powerupStickyBombs',
                        'powerupImpactBombs',
                        'powerupIceBombs',
                        'powerupHealth',
                        'powerupLandMines',
                        'bombColorIce',
                        'achievementMine',
                    )
                    args[0].node.color_texture = bs.gettexture(choice(fake_tex))
            
            # if powertype is default we do Nothing 
        return wrapper

    # replace original one to custom one
    bascenev1lib.actor.powerupbox.PowerupBox.__init__ = pbx_new_init(bascenev1lib.actor.powerupbox.PowerupBox.__init__)
    
    # adding some attributes in Spaz __init__ function that we need
    def spaz_new_init(func):
        def wrapper(*args, **kwargs):
        
            # original code
            func(*args, **kwargs)
            
            args[0].bomb_counter: int = 0
            args[0].last_bomb_count: int | None = None
            args[0].last_counter_tex: babase.Texture | None = None
            
            args[0].invisible_wear_off_flash_timer: bs.Timer | None = None
            args[0].invisible_wear_off_timer: bs.Timer | None = None
            args[0].invisible: bool = False
            
            
        return wrapper
    # replace original one to custome one
    bascenev1lib.actor.spaz.Spaz.__init__ = spaz_new_init(bascenev1lib.actor.spaz.Spaz.__init__)

    # Spaz 
    def spaz_new_handlemessage(func):
        def wrapper(*args, **kwargs):
            # only rect to bs.PowerupMessage
            if isinstance(args[1], bs.PowerupMessage):
                    
                    if args[1].poweruptype == 'random':
                        # Only Postive powerups
                        powerups = (
                            'health',
                            'ice_bombs',
                            'impact_bombs',
                            'sticky_bombs',
                            'punch',
                            'shield',
                            'ice_impact_bombs',
                            'ice_mine',
                            'invisible',
                        )
                        random_powerup = choice(powerups)
                        args[0].node.handlemessage(bs.PowerupMessage(random_powerup))
                        
                        # Let's add popuptext to know that which powerup we get 
                        PopupText(
                            text = random_powerup.upper(),
                            position = args[0].node.position,
                            random_offset = 0.0,
                            scale = 2.0,
                        ).autoretain()
                    # annoying powerup
                    elif args[1].poweruptype == 'fake':
                        
                        # if player have shields so our blast and freeze no longer work
                        if not args[0].shield:
                            danger = choice(['blast', 'freeze'])
                        
                            if danger == "blast":
                                Blast(
                                    position = args[0].node.position,
                                    velocity = args[0].node.velocity,
                                    blast_radius = 0.7,
                                    blast_type = 'land_mine',
                                ).autoretain()
                        
                                PopupText(
                                   text = "Boom!",
                                   position = args[0].node.position,
                                   random_offset = 0.0,
                                   scale = 2.0,
                                   color = (1.0, 0.0, 0.0)
                                ).autoretain()
                                
                            elif danger == 'freeze':
                                args[0].node.handlemessage(bs.FreezeMessage())
                            
                                PopupText(
                                    text = "So Cold!",
                                    position = args[0].node.position,
                                    random_offset = 0.0,
                                    scale = 2.0,
                                    color = (0.0, 0.5, 1.0)
                                ).autoretain()
                            
                                # emit some Cold chunk 
                                bs.emitfx(
                                   position = args[0].node.position,
                                   velocity = args[0].node.velocity,
                                   count =  10,
                                   scale = 0.6,
                                   spread = 0.4,
                                   chunk_type = 'ice',
                               )
                            # let's also provide shield to get hope
                            def shield_time() -> NoReturn:
                                args[0].node.handlemessage(bs.PowerupMessage('shield'))
                            # only run if player is alive 
                            if args[0].node:
                                # needd little bit delay cause our code run first 
                                bs.timer(0.1, shield_time)
                        # if player have shield with good hitpoint so we remove it
                        # shield max hitpoint = 575
                        elif args[0].shield_hitpoints > 575/2:
                            args[0].shield_hitpoints = -1
                            
                            PopupText(
                                    text = "i eat your shield!",
                                    position = args[0].node.position,
                                    random_offset = 0.0,
                                    scale = 2.0,
                                    color = (0.0, 0.5, 1.0)
                                ).autoretain()
                        # else player have low shield hitpoint so we knockout him
                        else:
                            args[0].node.handlemessage('knockout', 5000)
                            
                            PopupText(
                                    text = "GoodNight!",
                                    position = args[0].node.position,
                                    random_offset = 0.0,
                                    scale = 2.0,
                                    color = (0.0, 0.5, 1.0)
                                ).autoretain()
                    elif args[1].poweruptype == 'invisible':
                        # what if player mesh remove two times? 
                        if args[0].invisible == False:
                            tex = bs.gettexture('scrollWidgetGlow')
                            args[0]._flash_billboard(tex)
                            args[0].invisible = True
                            Plugin.remove_meshs(args[0])
                        
                            if args[0].powerups_expire:
                                args[0].node.mini_billboard_3_texture = tex
                                t_ms = bs.time() * 1000
                                assert isinstance(t_ms, int)
                                args[0].node.mini_billboard_3_start_time = t_ms
                                args[0].node.mini_billboard_3_end_time = (
                                    t_ms + 15000
                                )
                                args[0].invisible_wear_off_flash_timer = bs.Timer(
                                    15000 - 2000,
                                    babase.Call(Plugin.invisible_wear_off_flash, args[0]),
                                    timeformat=babase.TimeFormat.MILLISECONDS,
                                 )
                                args[0].invisible_wear_off_timer = bs.Timer(
                                    15000,
                                     babase.Call(Plugin.invisible_wear_off, args[0]),
                                     timeformat=babase.TimeFormat.MILLISECONDS,
                                 )
                        # lets gives negative powerup
                        else:
                            args[0].node.handlemessage(bs.PowerupMessage('fake'))
                    elif args[1].poweruptype == 'ice_impact_bombs':
                        tex = bs.gettexture('bombColorIce')
                        Plugin.set_bomb_count(args[0], 3, 'ice_impact', tex)
                        
                        args[0].last_bomb_count = 'ice_impact'
                        args[0].last_counter_tex = tex
                        # need to reset our other counter
                        args[0].land_mine_count = 0
                        
                    elif args[1].poweruptype == 'ice_mines':
                        tex = bs.gettexture('achievementMine')
                        Plugin.set_bomb_count(args[0], 3, 'ice_mine', tex)
                        
                        args[0].last_bomb_count = 'ice_mine'
                        args[0].last_counter_tex = tex
                        # need to reset our other counter
                        args[0].land_mine_count = 0

                    elif args[1].poweruptype == 'land_mines':
                        # need to reset our other counter
                        args[0].bomb_counter = 0
                    # if invisible is active let's also hide Boxing gloves 
                    elif args[1].poweruptype == 'punch':
                        if args[0].invisible:
                            def glove_timer() -> NoReturn:
                                args[0].node.boxing_gloves = False
                            # need little bit delay cause our code run first 
                            bs.timer(0.1, glove_timer)
                        
            # orignal code
            func(*args, **kwargs)
            
        return wrapper
    
    # replace original one to custom one
    bascenev1lib.actor.spaz.Spaz.handlemessage = spaz_new_handlemessage(bascenev1lib.actor.spaz.Spaz.handlemessage)
    
    # new_bomb_drop for Our custom Bombs
    def new_bomb_drop(func):
        def wrapper(*args):
            
            from bascenev1lib.actor.spaz import BombDiedMessage
            # add custom non counter bomb string in this empty tuple
            custom_bomb = ()
            
            if args[0].bomb_counter > 0 or args[0].bomb_type in custom_bomb:
            
                if args[0].frozen or args[0].bomb_count <= 0:
                     return None

                assert args[0].node

                pos = args[0].node.position_forward
                vel = args[0].node.velocity

                if args[0].bomb_counter > 0:
                    bomb_type = Plugin.set_bomb_count(args[0], args[0].bomb_counter - 1, args[0].last_bomb_count, args[0].last_counter_tex)
                    dropping_bomb = False
                else:
                    dropping_bomb = True
                    bomb_type = args[0].bomb_type

                bomb = custom_bomb(
                    position = (pos[0], pos[1], pos[2]),
                    velocity = (vel[0], vel[1], vel[2]),
                    bomb_type = bomb_type,
                    blast_radius = args[0].blast_radius,
                    source_player = args[0].source_player,
                    owner = args[0].node,
                ).autoretain()
                
                assert bomb.node
                
                if dropping_bomb:
                    args[0].bomb_count -= 1
                    bomb.node.add_death_action(
                         bs.WeakCall(args[0].handlemessage, BombDiedMessage())
                    )
                
                args[0]._pick_up(bomb.node)
                
                return bomb
                
            else:
                # Original Code
                # only run when bomb type is default
                func(*args)
               
        return wrapper

    bascenev1lib.actor.spaz.Spaz.drop_bomb = new_bomb_drop(bascenev1lib.actor.spaz.Spaz.drop_bomb)
    
    # because of my laziness i replace whole function
    # but in future i most probably change it
    # this function is bot ai Updater 
    def _update(self) -> None:

        # Update one of our bot lists each time through.
        # First off, remove no-longer-existing bots from the list.
        try:
            bot_list = self._bot_lists[self._bot_update_list] = [
                b for b in self._bot_lists[self._bot_update_list] if b
            ]
        except Exception:
            bot_list = []
            babase.print_exception(
                'Error updating bot list: '
                + str(self._bot_lists[self._bot_update_list])
            )
        self._bot_update_list = (
            self._bot_update_list + 1
        ) % self._bot_list_count

        # Update our list of player points for the bots to use.
        player_pts = []
        for player in bs.getactivity().players:
            assert isinstance(player, bs.Player)
            try:
                # TODO: could use abstracted player.position here so we
                # don't have to assume their actor type, but we have no
                # abstracted velocity as of yet.
                if player.is_alive() and not player.actor.invisible:
                    assert isinstance(player.actor, Spaz)
                    assert player.actor.node
                    player_pts.append(
                        (
                            babase.Vec3(player.actor.node.position),
                            babase.Vec3(player.actor.node.velocity),
                        )
                    )
            except Exception:
                babase.print_exception('Error on bot-set _update.')

        for bot in bot_list:
            bot.set_player_points(player_pts)
            bot.update_ai()

    bascenev1lib.actor.spazbot.SpazBotSet._update = _update
    
    def remove_meshs(self) -> NoReturn:
        
        if self.node:
            self.head = self.node.head_mesh
            self.torso = self.node.torso_mesh
            self.pelvis = self.node.pelvis_mesh
            self.upper_arm = self.node.upper_arm_mesh
            self.upper_leg = self.node.upper_leg_mesh
            self.lower_leg = self.node.lower_leg_mesh
            self.forearm = self.node.forearm_mesh
            self.hand = self.node.hand_mesh
            self.toes = self.node.toes_mesh
            self.style = self.node.style
            self.name = self.node.name
            self.node.head_mesh = None
            self.node.torso_mesh = None
            self.node.pelvis_mesh = None
            self.node.upper_arm_mesh = None
            self.node.upper_leg_mesh = None
            self.node.lower_leg_mesh = None
            self.node.hand_mesh = None
            self.node.forearm_mesh = None
            self.node.toes_mesh = None
            self.node.style = 'ali'
            self.node.name = ''
            self.node.boxing_gloves = False

    def invisible_wear_off_flash(self) -> NoReturn:
        
        if self.node:
            self.node.billboard_texture = bs.gettexture('scrollWidgetGlow')
            self.node.billboard_opacity = 1.0
            self.node.billboard_cross_out = True

    def invisible_wear_off(self) -> NoReturn:
        
        if self.node:
            self.invisible = False
            self.node.billboard_opacity = 0.0
            self.node.head_mesh = self.head
            self.node.torso_mesh = self.torso
            self.node.pelvis_mesh = self.pelvis
            self.node.upper_arm_mesh = self.upper_arm
            self.node.upper_leg_mesh = self.upper_leg
            self.node.lower_leg_mesh = self.lower_leg
            self.node.hand_mesh = self.hand
            self.node.forearm_mesh = self.forearm
            self.node.toes_mesh = self.toes
            self.node.style = self.style
            self.node.name = self.name

    def set_bomb_count(self, count: int, bomb_type: str, tex: babase.Texture) -> bomb_type:
        """ bomb text counter """
 
        self.bomb_counter = count

        if self.node:
            if self.bomb_counter > 0:
                self.node.counter_text = 'x' + str(self.bomb_count)