#!/usr/bin/env python3
# -*- coding: ascii -*-
from re import sub

import pygame
import pygame_gui
import ujson
from pygame_gui.core import ObjectID

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import (
    UIImageButton,
    CatButton,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale_value,
)
from scripts.utility import ui_scale
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..game_structure.windows import PronounCreation
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.get_arrow import get_arrow

with open("resources/dicts/pronouns.json", "r", encoding="utf-8") as f:
    pronouns_dict = ujson.load(f)


class ChangeGenderScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat_button = None
        self.previous_cat_button = None
        self.back_button = None
        self.the_cat = None
        self.selected_cat_elements = {}
        self.buttons = {}
        self.next_cat = None
        self.previous_cat = None
        self.elements = {}
        self.windows = None
        self.removalboxes_text = {}
        self.removalbuttons = {}
        self.deletebuttons = {}
        self.addbuttons = {}
        self.pronoun_template = [
            {
                "subject": "",
                "object": "",
                "poss": "",
                "inposs": "",
                "self": "",
                "conju": 1,
            }
        ]
        self.remove_button = {}
        self.removalboxes_text = {}
        self.boxes = {}
        self.box_labels = {}
        self.conju = 2

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.update_selected_cat()
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_selected_cat()
            elif event.ui_element == self.buttons["save"]:
                if self.are_boxes_full():
                    gender_identity = self.get_new_identity()
                    self.the_cat.genderalign = gender_identity
                    self.selected_cat_elements["identity_changed"].show()
                    self.selected_cat_elements["cat_gender"].kill()
                    self.selected_cat_elements[
                        "cat_gender"
                    ] = pygame_gui.elements.UITextBox(
                        f"{self.the_cat.genderalign}",
                        ui_scale(pygame.Rect((126, 250), (250, 250))),
                        object_id=get_text_box_theme(
                            "#text_box_30_horizcenter_spacing_95"
                        ),
                        manager=MANAGER,
                    )

            elif event.ui_element == self.buttons["add_pronouns"]:
                PronounCreation(self.the_cat)
                self.previous_cat_button.disable()
                self.next_cat_button.disable()
                self.back_button.disable()

            elif type(event.ui_element) is CatButton:
                if event.ui_element.cat_id == "add":
                    if event.ui_element.cat_object not in self.the_cat.pronouns:
                        self.the_cat.pronouns.append(event.ui_element.cat_object)
                elif event.ui_element.cat_id == "remove":
                    if (
                        event.ui_element.cat_object in self.the_cat.pronouns
                        and len(self.the_cat.pronouns) > 1
                    ):
                        self.the_cat.pronouns.remove(event.ui_element.cat_object)
                elif event.ui_element.cat_id == "delete":
                    if event.ui_element.cat_object in game.clan.custom_pronouns:
                        game.clan.custom_pronouns.remove(event.ui_element.cat_object)

                self.update_selected_cat()

    def screen_switches(self):
        super().screen_switches()
        self.next_cat_button = UIImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "",
            object_id="#next_cat_button",
            manager=MANAGER,
        )
        self.previous_cat_button = UIImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "",
            object_id="#previous_cat_button",
            manager=MANAGER,
        )
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.update_selected_cat()

    def get_new_identity(self):
        new_gender_identity = [""]

        if (
            sub(r"[^A-Za-z0-9 ]+", "", self.selected_cat_elements["gender"].get_text())
            != ""
        ):
            new_gender_identity = sub(
                r"[^A-Za-z0-9 ]+", "", self.selected_cat_elements["gender"].get_text()
            )

        return new_gender_identity

    def is_box_full(self, entry):
        if entry.get_text() == "":
            return False
        else:
            return True

    def are_boxes_full(self):
        values = []
        values.append(self.is_box_full(self.selected_cat_elements["gender"]))
        for value in values:
            if value is False:
                return False
        return True

    def get_sample_text(self, pronouns):
        text = ""
        text += f"Demo: {pronouns['ID']} <br>"
        subject = f"{pronouns['subject']} are quick. <br>"
        if pronouns["conju"] == 2:
            subject = f"{pronouns['subject']} is quick. <br>"
        text += subject.capitalize()
        text += f"Everyone saw {pronouns['object']}. <br>"
        poss = f"{pronouns['poss']} paw slipped.<br>"
        text += poss.capitalize()
        text += f"That den is {pronouns['inposs']}. <br>"
        text += f"This cat hunts by {pronouns['self']}."
        return text

    def update_selected_cat(self):
        self.reset_buttons_and_boxes()

        self.the_cat = Cat.fetch_cat(game.switches["cat"])
        if not self.the_cat:
            return

        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 100), (699, 520))),
            pygame.transform.scale(
                pygame.image.load(
                    "resources/images/gender_framing.png"
                ).convert_alpha(),
                ui_scale_dimensions((699, 520)),
            ),
            manager=MANAGER,
        )
        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((180, 105), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        # In what case would a cat have no genderalign? -key
        if not self.the_cat.genderalign:
            text = f"{self.the_cat.gender}"
        else:
            text = f"{self.the_cat.genderalign}"

        self.selected_cat_elements["cat_gender"] = pygame_gui.elements.UITextBox(
            text,
            ui_scale(pygame.Rect((130, 250), (250, 250))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        name = str(self.the_cat.name)
        header = "Change " + name + "'s Gender"
        self.selected_cat_elements["header"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((245, 62), (325, 32))),
            header,
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
        )

        # Save Confirmation
        self.selected_cat_elements["identity_changed"] = pygame_gui.elements.UITextBox(
            "Gender identity changed!",
            ui_scale(pygame.Rect((385, 247), (400, 40))),
            visible=False,
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
        )

        self.selected_cat_elements["description"] = pygame_gui.elements.UITextBox(
            f"<br> You can set this to anything! "
            f"Gender identity does not affect gameplay.",
            ui_scale(pygame.Rect((312, 132), (330, 75))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
        )
        self.buttons["add_pronouns"] = UIImageButton(
            ui_scale(pygame.Rect((320, 645), (162, 28))),
            "",
            object_id="#add_pronouns_button",
            manager=MANAGER,
        )
        self.selected_cat_elements["gender"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((350, 220), (165, 30))),
            placeholder_text=self.the_cat.genderalign,
            manager=MANAGER,
        )
        self.buttons["save"] = UIImageButton(
            ui_scale(pygame.Rect((532, 220), (73, 30))),
            "",
            object_id="#save_button_pronoun",
            starting_height=2,
            manager=MANAGER,
        )
        self.determine_previous_and_next_cat()
        self.pronoun_update()
        self.preset_update()
        self.update_disabled_buttons()

    def update_disabled_buttons(self):
        # Previous and next cat button
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

    def pronoun_update(self):
        # List the various pronouns
        self.removalboxes_text[
            "container_general"
        ] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=ui_scale(pygame.Rect((50, 330), (337, 270))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER,
        )

        self.removalboxes_text["instr"] = pygame_gui.elements.UITextBox(
            "Current Pronouns",
            ui_scale(pygame.Rect((0, 297), (175, 32))),
            object_id=ObjectID("#text_box_34_horizcenter", "#dark"),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        n = 0
        ycoor = 4
        pronoun_frame = "resources/images/pronoun_frame.png"

        for pronounset in self.the_cat.pronouns:
            displayname = (
                f"{pronounset['subject']}/{pronounset['object']}/"
                f"{pronounset['inposs']}/{pronounset['self']}"
            )
            short_name = shorten_text_to_fit(displayname, 180, 13)

            # Create block for each pronounset with dynamic ycoor
            block_rect = ui_scale(pygame.Rect((75, ycoor), (272, 44)))
            self.elements[f"cat_pronouns_{n}"] = pygame_gui.elements.UIImage(
                block_rect,
                pygame.transform.scale(
                    pygame.image.load(pronoun_frame).convert_alpha(),
                    ui_scale_dimensions((272, 44)),
                ),
                container=self.removalboxes_text["container_general"],
                manager=MANAGER,
            )

            # Create remove button for each pronounset with dynamic ycoor
            # TODO: update this to use UISurfaceImageButton
            button_rect = ui_scale(pygame.Rect((275, ycoor + 9), (24, 24)))
            self.removalbuttons[f"cat_pronouns_{n}"] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="remove",
                container=self.removalboxes_text["container_general"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER,
            )

            # Create UITextBox for pronoun display with clickable remove button
            text_box_rect = ui_scale(pygame.Rect((50, ycoor + 2), (200, 39)))
            self.removalboxes_text[f"cat_pronouns_{n}"] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.removalboxes_text["container_general"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER,
            )

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            self.buttons[f"{n}_tooltip_cat_pronouns"] = UIImageButton(
                text_box_rect,
                "",
                object_id="#blank_button_small",
                container=self.removalboxes_text["container_general"],
                tool_tip_text=displayname if short_name != displayname else None,
                manager=MANAGER,
                starting_height=2,
            )

            n += 1
            ycoor += 52

        # Disable removing is a cat has only one pronoun.
        if n == 1:
            for button_id in self.removalbuttons:
                self.removalbuttons[button_id].disable()

        min_scrollable_height = max(100, n * 65)

        self.removalboxes_text["container_general"].set_scrollable_area_dimensions(
            ui_scale_dimensions((310, min_scrollable_height))
        )

    def preset_update(self):
        # List the various pronouns
        self.removalboxes_text[
            "container_general2"
        ] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=ui_scale(pygame.Rect((397, 330), (337, 270))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER,
        )

        self.removalboxes_text["instr2"] = pygame_gui.elements.UITextBox(
            "Saved Pronouns",
            ui_scale(pygame.Rect((500, 297), (175, 32))),
            object_id="#text_box_34_horizleft_dark",
            manager=MANAGER,
        )

        n = 0
        ycoor = 4
        pronoun_frame = "resources/images/pronoun_frame.png"

        all_pronouns = pronouns_dict["default_pronouns"] + [
            x
            for x in game.clan.custom_pronouns
            if x not in pronouns_dict["default_pronouns"]
        ]
        for pronounset in all_pronouns:
            displayname = (
                f"{pronounset['subject']}/{pronounset['object']}/"
                f"{pronounset['inposs']}/{pronounset['self']}"
            )
            short_name = shorten_text_to_fit(displayname, 140, 13)

            if pronounset in pronouns_dict["default_pronouns"]:
                dict_name_core = f"default_pronouns_{n}"
            else:
                dict_name_core = f"custom_pronouns_{n}"

            # Create block for each pronounset with dynamic ycoor
            block_rect = ui_scale(pygame.Rect((37, ycoor), (272, 44)))
            self.elements[f"{n}"] = pygame_gui.elements.UIImage(
                block_rect,
                pygame.transform.scale(
                    pygame.image.load(pronoun_frame).convert_alpha(),
                    ui_scale_dimensions((272, 44)),
                ),
                container=self.removalboxes_text["container_general2"],
                manager=MANAGER,
            )

            button_rect = ui_scale(pygame.Rect((212, ycoor + 7), (56, 28)))
            # TODO: update this to use UISurfaceImageButton
            self.addbuttons[dict_name_core] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="add",
                container=self.removalboxes_text["container_general2"],
                object_id="#add_button",
                starting_height=2,
                manager=MANAGER,
            )

            if pronounset in self.the_cat.pronouns:
                self.addbuttons[dict_name_core].disable()

            # Create UITextBox for pronoun display and create tooltip for full pronoun display
            button_rect = ui_scale(pygame.Rect((225, ycoor + 9), (24, 24)))
            text_box_rect = ui_scale(pygame.Rect((50, ycoor + 4), (200, 49)))
            self.removalboxes_text[dict_name_core] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.removalboxes_text["container_general2"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER,
            )

            self.removalboxes_text[dict_name_core].disable()

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            self.buttons["tooltip_" + dict_name_core] = UIImageButton(
                text_box_rect,
                "",
                object_id="#blank_button_small",
                container=self.removalboxes_text["container_general2"],
                tool_tip_text=displayname if short_name != displayname else None,
                manager=MANAGER,
                starting_height=2,
            )

            # Create remove button for each pronounset with dynamic ycoor
            self.deletebuttons[dict_name_core] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="delete",
                container=self.removalboxes_text["container_general2"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER,
            )
            # though we've made the remove button visible, it needs to be disabled so that the user cannnot remove
            # the defaults.  button is only visible here for UI consistency
            if pronounset in pronouns_dict["default_pronouns"]:
                self.deletebuttons[dict_name_core].disable()

            n += 1
            ycoor += 52

        min_scrollable_height = max(100, n * 65)

        self.removalboxes_text["container_general2"].set_scrollable_area_dimensions(
            (
                self.removalboxes_text["container_general2"].rect[2],
                ui_scale_value(min_scrollable_height),
            ),
        )

    def reset_buttons_and_boxes(self):
        # kills everything when switching cats
        for ele in self.elements:
            self.elements[ele].kill()
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        for ele in self.buttons:
            self.buttons[ele].kill()
        for ele in self.removalboxes_text:
            self.removalboxes_text[ele].kill()
        for ele in self.removalbuttons:
            self.removalbuttons[ele].kill()
        for ele in self.deletebuttons:
            self.deletebuttons[ele].kill()
        for ele in self.addbuttons:
            self.addbuttons[ele].kill()

        self.selected_cat_elements = {}
        self.removalboxes_text = {}
        self.addbuttons = {}
        self.elements = {}
        self.removalbuttons = {}
        self.deletebuttons = {}

    def determine_previous_and_next_cat(self):
        """Determines where the next and previous buttons point to."""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if (
            self.the_cat.dead
            and not is_instructor
            and self.the_cat.df == game.clan.instructor.df
            and not (self.the_cat.outside or self.the_cat.exiled)
        ):
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if (
                    next_cat == 0
                    and check_cat.ID != self.the_cat.ID
                    and check_cat.dead == self.the_cat.dead
                    and check_cat.ID != game.clan.instructor.ID
                    and check_cat.outside == self.the_cat.outside
                    and check_cat.df == self.the_cat.df
                    and not check_cat.faded
                ):
                    previous_cat = check_cat.ID

                elif (
                    next_cat == 1
                    and check_cat != self.the_cat.ID
                    and check_cat.dead == self.the_cat.dead
                    and check_cat.ID != game.clan.instructor.ID
                    and check_cat.outside == self.the_cat.outside
                    and check_cat.df == self.the_cat.df
                    and not check_cat.faded
                ):
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

    def exit_screen(self):
        # kill everything
        self.back_button.kill()
        del self.back_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.elements["cat_frame"].kill()
        del self.elements["cat_frame"]

        self.reset_buttons_and_boxes()
