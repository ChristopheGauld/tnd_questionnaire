"""Construit le questionnaire parent myHCL TND pour l'API v3 de Formbricks.

Le document source est myHCL_TND_courte_FORMBRICKS.docx. Les formulations
auto-rapportees ont ete adaptees pour que le parent reponde au sujet de son
enfant. Cette adaptation doit etre validee scientifiquement avant une etude.
"""

from __future__ import annotations

import hashlib
from typing import Any, Iterable


LANGUAGE = "fr-FR"
DUMMY_WORKSPACE_ID = "c00000000000000000000000"


def tr(text: str) -> dict[str, str]:
    return {LANGUAGE: text}


def stable_cuid(seed: str) -> str:
    """Return a deterministic CUID2-shaped identifier accepted by Formbricks."""

    return "c" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:23]


def choices(element_id: str, labels: Iterable[str]) -> list[dict[str, Any]]:
    return [
        {"id": f"{element_id}_c{index}", "label": tr(label)}
        for index, label in enumerate(labels, start=1)
    ]


def open_text(
    element_id: str,
    headline: str,
    *,
    subheader: str | None = None,
    input_type: str = "text",
    long_answer: bool = False,
    placeholder: str | None = None,
) -> dict[str, Any]:
    element: dict[str, Any] = {
        "id": element_id,
        "type": "openText",
        "headline": tr(headline),
        "required": True,
        "inputType": input_type,
        "longAnswer": long_answer,
    }
    if subheader:
        element["subheader"] = tr(subheader)
    if placeholder:
        element["placeholder"] = tr(placeholder)
    return element


def date_question(element_id: str, headline: str) -> dict[str, Any]:
    return {
        "id": element_id,
        "type": "date",
        "headline": tr(headline),
        "required": True,
        "format": "d-M-y",
    }


def single_choice(
    element_id: str,
    headline: str,
    labels: Iterable[str],
    *,
    subheader: str | None = None,
) -> dict[str, Any]:
    element: dict[str, Any] = {
        "id": element_id,
        "type": "multipleChoiceSingle",
        "headline": tr(headline),
        "required": True,
        "choices": choices(element_id, labels),
        "shuffleOption": "none",
        "displayType": "list",
    }
    if subheader:
        element["subheader"] = tr(subheader)
    return element


def matrix(
    element_id: str,
    headline: str,
    row_labels: Iterable[str],
    column_labels: Iterable[str],
    *,
    subheader: str | None = None,
) -> dict[str, Any]:
    rows = list(row_labels)
    element: dict[str, Any] = {
        "id": element_id,
        "type": "matrix",
        "headline": tr(headline),
        "required": True,
        "rows": [
            {"id": f"{element_id}_r{index}", "label": tr(label)}
            for index, label in enumerate(rows, start=1)
        ],
        "columns": [
            {"id": f"{element_id}_c{index}", "label": tr(label)}
            for index, label in enumerate(column_labels, start=1)
        ],
        "shuffleOption": "none",
        "validation": {
            "logic": "and",
            "rules": [
                {
                    "id": f"{element_id}_all_rows",
                    "type": "answerAllRows",
                    "params": {},
                }
            ],
        },
    }
    if subheader:
        element["subheader"] = tr(subheader)
    return element


def block(name: str, elements: list[dict[str, Any]], *, final: bool = False) -> dict[str, Any]:
    return {
        "name": name,
        "elements": elements,
        "buttonLabel": tr("Envoyer mes réponses" if final else "Enregistrer et continuer"),
        "backButtonLabel": tr("Retour"),
    }


CONNERS = [
    "L'enfant est agité ou très actif.",
    "L'enfant est nerveux ou impulsif.",
    "L'enfant ne finit pas ce qu'il a commencé et son attention est de courte durée.",
    "L'enfant est toujours remuant.",
    "L'enfant perturbe les autres enfants.",
    "L'enfant est inattentif et facilement distrait.",
    "Ses demandes doivent être immédiatement satisfaites et il est facilement frustré.",
    "L'enfant pleure souvent et facilement.",
    "L'enfant a des changements d'humeur rapides et marqués.",
    "L'enfant a des accès de colère, avec un comportement explosif et imprévisible.",
]


SNAP_IV = [
    "1. Souvent, votre enfant ne parvient pas à prêter attention aux détails ou commet des fautes d'étourderie dans ses travaux scolaires.",
    "2. Votre enfant a souvent de la difficulté à soutenir son attention dans les tâches ou dans les jeux.",
    "3. Votre enfant semble souvent ne pas écouter lorsqu'on lui parle personnellement.",
    "4. Souvent, votre enfant ne se conforme pas aux consignes et ne parvient pas à terminer ses travaux scolaires.",
    "5. Votre enfant a souvent de la difficulté à organiser ses tâches ou ses activités.",
    "6. Souvent, votre enfant évite, a en aversion ou fait à contrecœur les tâches qui nécessitent un effort mental soutenu.",
    "7. Votre enfant perd souvent les objets nécessaires à ses tâches ou activités, par exemple ses devoirs, stylos ou livres.",
    "8. Votre enfant se laisse souvent distraire par des stimuli externes.",
    "9. Votre enfant a des oublis fréquents dans les activités de la vie quotidienne.",
    "10. Votre enfant agite souvent les mains ou les pieds.",
    "11. Votre enfant se lève souvent en classe alors qu'il devrait rester assis.",
    "12. Souvent, votre enfant court ou grimpe partout dans des situations où cela est inapproprié.",
    "13. Votre enfant a souvent du mal à se tenir tranquille dans les jeux ou les activités de loisirs.",
    "14. Votre enfant est souvent en mouvement ou agit souvent comme s'il était monté sur des ressorts.",
    "15. Votre enfant parle souvent trop.",
    "16. Votre enfant laisse souvent échapper la réponse à une question qui n'est pas encore entièrement posée.",
    "17. Votre enfant a souvent de la difficulté à attendre son tour.",
    "18. Votre enfant interrompt souvent les autres ou impose sa présence, par exemple dans les conversations ou les jeux.",
    "19. Votre enfant se met souvent en colère.",
    "20. Votre enfant conteste souvent ce que disent les adultes.",
    "21. Votre enfant s'oppose souvent activement ou refuse de se plier aux demandes ou aux règles des adultes.",
    "22. Votre enfant contrarie souvent les autres délibérément.",
    "23. Votre enfant fait souvent porter aux autres la responsabilité de ses erreurs ou de sa mauvaise conduite.",
    "24. Votre enfant est souvent susceptible ou facilement agacé par les autres.",
    "25. Votre enfant est souvent fâché et plein de ressentiment.",
    "26. Votre enfant se montre souvent méchant ou vindicatif, avec l'envie de se venger.",
]


SLEEP_FREQUENCY = ["Jamais", "Rarement", "Parfois", "Souvent", "Toujours"]
SLEEP_ITEMS = [
    "3. L'enfant va au lit avec réticence.",
    "4. L'enfant a des difficultés à s'endormir.",
    "5. L'enfant ressent de l'anxiété ou des peurs au moment de s'endormir.",
    "6. Lorsque l'enfant s'endort, il semble vivre ses rêves.",
    "7. L'enfant transpire excessivement à l'endormissement.",
    "8. L'enfant se réveille plus de deux fois par nuit.",
    "9. L'enfant a des difficultés à s'endormir à nouveau après s'être réveillé dans la nuit.",
    "10. Dans son sommeil, l'enfant a des mouvements brusques ou des secousses des jambes, change souvent de position ou jette les couvertures au pied du lit.",
    "11. L'enfant a des difficultés à respirer durant la nuit.",
    "12. L'enfant fait des pauses respiratoires ou cherche sa respiration pendant son sommeil.",
    "13. L'enfant ronfle.",
    "14. L'enfant transpire excessivement pendant la nuit.",
    "15. Vous avez assisté à un épisode de somnambulisme de l'enfant : il se lève et déambule pendant son sommeil.",
    "16. Vous avez déjà entendu l'enfant parler dans son sommeil.",
    "17. L'enfant grince des dents pendant son sommeil.",
    "18. L'enfant se réveille en hurlant ou est si confus qu'il est impossible de l'approcher, mais il n'a aucun souvenir de ces événements le matin suivant.",
    "19. L'enfant fait des cauchemars dont il ne se rappelle pas le matin venu.",
    "20. L'enfant est difficile à réveiller le matin.",
    "21. L'enfant se réveille le matin en se sentant fatigué.",
    "22. L'enfant se sent incapable de bouger quand il se réveille le matin.",
    "23. L'enfant est somnolent durant la journée.",
    "24. L'enfant s'endort brutalement, de façon inattendue, à l'école ou lors de ses activités.",
    "25. Lorsque l'enfant rit, il a une perte de tonus musculaire pouvant entraîner un affaiblissement du corps ou une chute.",
]


EPWORTH = [
    "1. Assis en train de lire.",
    "2. Assis en train de regarder la télévision ou une vidéo.",
    "3. Assis inactif dans un lieu public, par exemple au cinéma ou dans une salle d'attente.",
    "4. Assis en voiture ou en bus pour un trajet d'environ une heure.",
    "5. Allongé pour se reposer ou faire la sieste l'après-midi.",
    "6. Assis en train de parler à quelqu'un.",
    "7. Assis seul après le repas.",
    "8. Assis à l'école, en classe le matin ou l'après-midi.",
]


HAD = [
    (
        "1. Votre enfant se sent tendu ou énervé.",
        ["Jamais", "De temps en temps", "Souvent", "La plupart du temps"],
    ),
    (
        "2. Votre enfant prend plaisir aux mêmes choses qu'autrefois.",
        ["Oui, tout autant qu'avant", "Pas autant", "Un peu seulement", "Presque plus"],
    ),
    (
        "3. Votre enfant a une sensation de peur comme si quelque chose d'horrible allait arriver.",
        ["Pas du tout", "Un peu, sans inquiétude", "Oui, mais ce n'est pas trop grave", "Oui, très nettement"],
    ),
    (
        "4. Votre enfant rit et voit le bon côté des choses.",
        ["Autant que par le passé", "Pas autant qu'avant", "Vraiment moins qu'avant", "Plus du tout"],
    ),
    (
        "5. Votre enfant se fait du souci.",
        ["Très occasionnellement", "Occasionnellement", "Assez souvent", "Très souvent"],
    ),
    (
        "6. Votre enfant est de bonne humeur.",
        ["La plupart du temps", "Assez souvent", "Rarement", "Jamais"],
    ),
    (
        "7. Votre enfant peut rester tranquillement assis sans rien faire et se sentir décontracté.",
        ["Oui, quoi qu'il arrive", "Oui, en général", "Rarement", "Jamais"],
    ),
    (
        "8. Votre enfant donne l'impression de fonctionner au ralenti.",
        ["Jamais", "Parfois", "Très souvent", "Presque toujours"],
    ),
    (
        "9. Votre enfant éprouve des sensations de peur et a l'estomac noué.",
        ["Jamais", "Parfois", "Assez souvent", "Très souvent"],
    ),
    (
        "10. Votre enfant ne s'intéresse plus à son apparence.",
        [
            "Il y prête autant d'attention que par le passé",
            "Il se peut qu'il n'y fasse plus autant attention",
            "Il n'y apporte pas autant d'attention qu'il devrait",
            "Plus du tout",
        ],
    ),
    (
        "11. Votre enfant a la bougeotte et n'arrive pas à tenir en place.",
        ["Pas du tout", "Pas tellement", "Un peu", "Oui, tout à fait"],
    ),
    (
        "12. Votre enfant se réjouit d'avance à l'idée de faire certaines choses.",
        ["Autant qu'avant", "Un peu moins qu'avant", "Bien moins qu'avant", "Presque jamais"],
    ),
    (
        "13. Votre enfant éprouve des sensations soudaines de panique.",
        ["Jamais", "Pas très souvent", "Assez souvent", "Vraiment très souvent"],
    ),
    (
        "14. Votre enfant peut prendre plaisir à un bon livre ou à une bonne émission de télévision.",
        ["Souvent", "Parfois", "Rarement", "Très rarement"],
    ),
]


SRS = [
    "1. Semble beaucoup plus nerveux dans des situations sociales que lorsqu'il est seul.",
    "2. Son expression faciale n'est pas en harmonie avec ce qu'il dit.",
    "3. Semble avoir confiance en lui quand il interagit avec les autres.",
    "4. Quand il est stressé, l'enfant semble fonctionner en pilote automatique ou présente des comportements rigides qui paraissent étranges.",
    "5. Ne réalise pas que les autres essaient de se servir de lui.",
    "6. Préfère être seul plutôt qu'avec les autres.",
    "7. Est conscient de ce que les autres pensent ou ressentent.",
    "8. Se comporte de façon étrange ou bizarre.",
    "9. S'accroche aux adultes et semble trop dépendant d'eux.",
    "10. Interprète les choses de manière trop littérale et ne comprend pas le sens réel des conversations.",
    "11. A confiance en lui.",
    "12. Est capable de communiquer ses sentiments aux autres.",
    "13. Est maladroit dans les interactions impliquant un tour de rôle avec les personnes de son âge, par exemple dans les tours de parole.",
    "14. Est maladroit ou mal coordonné dans les activités physiques.",
    "15. Est capable de comprendre la signification du ton de la voix et de l'expression faciale des autres.",
    "16. Évite le contact visuel ou a un contact visuel inhabituel.",
    "17. Reconnaît lorsque quelque chose est injuste.",
    "18. A du mal à se faire des amis, même quand il fait de son mieux.",
    "19. A des difficultés à transmettre ses idées au cours d'une conversation.",
    "20. Présente des intérêts sensoriels inhabituels, comme faire tourner des objets ou les mettre dans sa bouche, ou des manières étranges de jouer.",
    "21. Est capable d'imiter les actions des autres.",
    "22. Joue de manière appropriée avec les enfants de son âge.",
    "23. Ne se joint pas aux activités des autres sauf si on le lui demande.",
    "24. A plus de difficulté que les autres enfants à modifier ses routines.",
    "25. Ne se soucie pas d'être en phase ou sur la même longueur d'onde que les autres.",
    "26. Offre du réconfort aux autres quand ils sont tristes.",
    "27. Évite d'initier des interactions sociales avec les autres.",
    "28. Pense ou parle de la même chose de manière répétitive.",
    "29. Est considéré par les autres enfants comme étrange ou bizarre.",
    "30. Est souvent dépassé par les situations où il se passe beaucoup de choses en même temps.",
    "31. Ne peut pas s'arrêter de penser à quelque chose une fois qu'il a commencé.",
    "32. A une bonne hygiène personnelle.",
    "33. Est socialement maladroit, même quand il essaie d'être poli.",
    "34. Évite les personnes qui veulent être proches émotionnellement de lui.",
    "35. A du mal à suivre le rythme d'une conversation normale.",
    "36. A des difficultés à entrer en relation avec les adultes.",
    "37. A des difficultés à entrer en relation avec les personnes de son âge.",
    "38. Réagit de manière appropriée aux changements d'humeur des autres, par exemple lorsqu'un camarade qui était content devient triste.",
    "39. A une variété d'intérêts restreinte.",
    "40. A de l'imagination et est à l'aise dans les jeux de faire semblant, sans perdre le contact avec la réalité.",
    "41. Semble sans but et passe passivement d'une activité à l'autre.",
    "42. Semble extrêmement sensible aux sons, aux textures ou aux odeurs.",
    "43. Se sépare facilement des personnes qui s'occupent de lui.",
    "44. Ne comprend pas les relations entre les événements d'une manière appropriée à son âge, par exemple en mélangeant les causes et les conséquences.",
    "45. Prête attention à des choses qui intéressent les autres, par exemple en regardant dans la même direction qu'eux.",
    "46. A une expression faciale trop sérieuse.",
    "47. Fait le sot ou rit de manière inappropriée.",
    "48. A le sens de l'humour et comprend les plaisanteries.",
    "49. A des aptitudes très supérieures à la moyenne dans certains domaines précis, tandis que son fonctionnement dans la plupart des tâches n'est pas bon.",
    "50. A des comportements répétitifs inhabituels, comme agiter les mains ou se balancer.",
    "51. A des difficultés à répondre directement aux questions et tourne autour du sujet.",
    "52. Est conscient lorsqu'il parle trop fort ou fait trop de bruit.",
    "53. Parle avec une tonalité vocale inhabituelle, par exemple comme un robot ou comme s'il donnait un cours.",
    "54. Semble utiliser les personnes comme si elles étaient des objets.",
    "55. Se rend compte lorsqu'il est trop proche ou envahit l'espace d'autrui.",
    "56. Marche entre deux personnes en train de parler.",
    "57. Est souvent l'objet de moqueries.",
    "58. Se concentre de manière inadaptée sur des parties d'objets au lieu d'en voir la totalité.",
    "59. Est trop soupçonneux.",
    "60. Est émotionnellement distant et montre peu ses émotions.",
    "61. Est inflexible et a du mal à changer d'opinion.",
    "62. Donne des raisons inhabituelles ou illogiques pour faire certaines choses.",
    "63. Touche les autres de manière inadaptée, par exemple pour établir un contact puis s'en va sans rien dire.",
    "64. Est trop tendu dans les situations sociales.",
    "65. Regarde ou fixe les autres de manière inappropriée.",
]


SCQ = [
    "1. Actuellement, votre enfant utilise-t-il au moins des phrases courtes lorsqu'il parle ?",
    "2. Pouvez-vous avoir avec lui une conversation dans laquelle chacun parle à son tour et rebondit sur ce que l'autre a dit ?",
    "3. A-t-il déjà dit des phrases étranges ou répété régulièrement la même chose, toujours de la même façon ?",
    "4. A-t-il déjà posé des questions ou fait des commentaires inappropriés, par exemple à des moments inopportuns ?",
    "5. A-t-il déjà utilisé les pronoms de manière incorrecte, par exemple en disant « tu » ou « il » pour parler de lui-même ?",
    "6. Lui est-il déjà arrivé d'utiliser des mots qu'il semblait avoir inventés ou de dire des choses de manière métaphorique, par exemple « pluie chaude » pour « vapeur » ?",
    "7. Lui est-il déjà arrivé de répéter des choses exactement de la même manière ou d'insister pour que vous répétiez inlassablement la même chose ?",
    "8. Y a-t-il déjà eu des choses qu'il semblait devoir faire d'une manière particulière ou selon un certain ordre, ou des rituels qu'il vous demandait de reproduire avec insistance ?",
    "9. Ses expressions faciales vous ont-elles habituellement semblé adaptées aux situations ?",
    "10. A-t-il déjà utilisé votre main comme un outil ou comme une partie de son propre corps, par exemple pour pointer ou vous faire ouvrir une porte ?",
    "11. A-t-il déjà eu des intérêts qui le préoccupaient et paraissaient étranges aux autres, par exemple les feux de circulation, les tuyaux ou les horaires ?",
    "12. A-t-il déjà été plus intéressé par une partie d'un jouet ou d'un objet que par son utilisation habituelle ?",
    "13. A-t-il déjà eu des intérêts adaptés à son âge mais inhabituels par leur intensité, par exemple les trains ou les dinosaures ?",
    "14. A-t-il déjà manifesté un intérêt inhabituel pour la vue, la sensation, le son, le goût ou l'odeur des choses ou d'une personne ?",
    "15. A-t-il déjà eu des maniérismes ou une façon étrange de bouger les mains ou les doigts ?",
    "16. A-t-il déjà eu des mouvements complexes de l'ensemble du corps, comme faire la toupie ou sauter sur place de manière répétitive ?",
    "17. S'est-il déjà fait mal volontairement, par exemple en se mordant les bras ou en se tapant la tête ?",
    "18. A-t-il déjà eu un objet, autre qu'une peluche, un doudou ou une couverture, qu'il devait emmener partout ?",
    "19. A-t-il des amis proches ou un meilleur ami ?",
    "20. Entre 4 et 5 ans, lui arrivait-il de bavarder avec vous simplement pour être agréable, sans chercher à obtenir quelque chose ?",
    "21. Entre 4 et 5 ans, lui arrivait-il de vous imiter spontanément, ou d'imiter d'autres personnes et leurs activités ?",
    "22. Entre 4 et 5 ans, lui arrivait-il de pointer spontanément des choses autour de lui simplement pour vous les montrer ?",
    "23. Entre 4 et 5 ans, lui arrivait-il d'utiliser des gestes autres que pointer ou tirer votre main pour vous faire savoir ce qu'il voulait ?",
    "24. Entre 4 et 5 ans, faisait-il « oui » de la tête ?",
    "25. Entre 4 et 5 ans, faisait-il « non » de la tête ?",
    "26. Entre 4 et 5 ans, vous regardait-il directement dans les yeux lorsqu'il faisait quelque chose avec vous ou vous parlait ?",
    "27. Entre 4 et 5 ans, souriait-il en réponse à quelqu'un qui lui souriait ?",
    "28. Entre 4 et 5 ans, lui arrivait-il de montrer des choses qui l'intéressaient pour attirer votre attention ?",
    "29. Entre 4 et 5 ans, lui arrivait-il de partager des choses autres que de la nourriture ?",
    "30. Entre 4 et 5 ans, lui arrivait-il de partager avec vous son plaisir ou sa joie ?",
    "31. Entre 4 et 5 ans, lui arrivait-il de vous réconforter si vous étiez triste ou blessé ?",
    "32. Entre 4 et 5 ans, lorsqu'il voulait quelque chose ou avait besoin d'aide, vous regardait-il en faisant des gestes accompagnés de sons ou de mots pour attirer votre attention ?",
    "33. Entre 4 et 5 ans, montrait-il une variété habituelle d'expressions faciales ?",
    "34. Entre 4 et 5 ans, lui arrivait-il de se joindre spontanément à des jeux sociaux et d'essayer d'imiter les actions ?",
    "35. Entre 4 et 5 ans, jouait-il à des jeux de faire semblant ?",
    "36. Entre 4 et 5 ans, semblait-il intéressé par les autres enfants de son âge qu'il ne connaissait pas ?",
    "37. Entre 4 et 5 ans, réagissait-il positivement lorsqu'un enfant l'approchait ?",
    "38. Entre 4 et 5 ans, si vous entriez dans une pièce et commenciez à lui parler sans l'appeler par son prénom, levait-il généralement les yeux et faisait-il attention à vous ?",
    "39. Entre 4 et 5 ans, lui arrivait-il de participer à des jeux imaginatifs avec d'autres enfants, chacun comprenant le rôle de l'autre ?",
    "40. Entre 4 et 5 ans, jouait-il à des jeux coopératifs nécessitant son intégration dans un groupe, comme cache-cache ou des jeux de ballon ?",
]


CAMOUFLAGE = [
    "1. Votre enfant copie intentionnellement le langage corporel ou les expressions faciales d'une personne avec laquelle il interagit.",
    "2. Votre enfant apprend comment les personnes utilisent leur corps et leur visage pour interagir en regardant la télévision ou des films, ou en lisant des romans.",
    "3. Votre enfant a essayé d'améliorer sa compréhension des compétences sociales en observant les autres.",
    "4. Votre enfant répète des phrases dites par d'autres personnes exactement comme il les a entendues la première fois.",
    "5. Votre enfant s'entraîne afin que ses expressions faciales et son langage corporel paraissent naturels.",
    "6. Votre enfant apprend des compétences sociales en regardant des émissions ou des films et essaie de les utiliser dans ses interactions.",
    "7. Dans ses interactions sociales, votre enfant utilise des comportements appris en regardant d'autres personnes interagir.",
    "8. Votre enfant a recherché les règles des interactions sociales, par exemple dans des livres, afin d'améliorer ses compétences sociales.",
    "9. Votre enfant a développé un scénario à suivre dans certaines situations sociales, par exemple une liste de questions ou de sujets.",
    "10. Votre enfant fait attention à son langage corporel ou à ses expressions faciales pour avoir l'air plus détendu.",
    "11. Votre enfant ajuste son langage corporel ou ses expressions faciales pour avoir l'air détendu.",
    "12. Votre enfant observe son langage corporel ou ses expressions faciales afin d'avoir l'air intéressé par la personne avec laquelle il interagit.",
    "13. Votre enfant ajuste son langage corporel ou ses expressions faciales pour avoir l'air intéressé par la personne avec laquelle il interagit.",
    "14. Votre enfant ne ressent pas le besoin de regarder les autres dans les yeux s'il n'en a pas envie.",
    "15. Dans les interactions sociales, votre enfant ne semble pas avoir conscience de ce que font son visage et son corps.",
    "16. Votre enfant pense toujours à l'impression qu'il fait aux autres.",
    "17. Votre enfant semble toujours conscient de l'impression qu'il fait aux autres.",
    "18. Votre enfant ressent rarement le besoin de jouer un rôle pour s'en sortir dans une situation sociale.",
    "19. Lorsqu'il parle avec les autres, la conversation semble se dérouler naturellement pour votre enfant.",
    "20. Dans des situations sociales, votre enfant essaie de trouver des moyens d'éviter d'interagir avec les autres.",
    "21. Dans les situations sociales, votre enfant donne l'impression de devoir jouer un rôle plutôt que d'être lui-même.",
    "22. Dans les situations sociales, votre enfant semble devoir se forcer à interagir avec les autres.",
    "23. Dans les situations sociales, votre enfant semble faire semblant d'être « normal ».",
    "24. Votre enfant a besoin du soutien d'autres personnes pour socialiser.",
    "25. Votre enfant se sent libre d'être lui-même lorsqu'il est avec d'autres personnes.",
]


ECO_ANXIETY = [
    "1. Il est difficile à votre enfant de se concentrer lorsqu'il pense au changement climatique.",
    "2. Il est difficile à votre enfant de s'endormir lorsqu'il pense au changement climatique.",
    "3. Votre enfant fait des cauchemars à propos du changement climatique.",
    "4. Votre enfant se retrouve à pleurer à cause du changement climatique.",
    "5. Votre enfant se demande pourquoi il n'arrive pas à mieux gérer ses préoccupations liées au changement climatique.",
    "6. Votre enfant se met à l'écart et pense aux raisons pour lesquelles il se sent ainsi face au changement climatique.",
    "7. Votre enfant écrit ses réflexions sur le changement climatique et les analyse.",
    "8. Votre enfant se demande pourquoi il réagit ainsi au changement climatique.",
    "9. Ses préoccupations au sujet du changement climatique l'empêchent de s'amuser avec sa famille ou ses amis.",
    "10. Votre enfant a du mal à trouver un équilibre entre ses préoccupations pour le développement durable et les besoins de sa famille.",
    "11. Ses préoccupations à propos du changement climatique interfèrent avec sa capacité à faire son travail ou ses tâches scolaires.",
    "12. Ses préoccupations concernant le changement climatique affectent négativement sa capacité à exploiter pleinement son potentiel.",
    "13. Ses amis disent qu'il pense trop au changement climatique.",
    "14. Votre enfant a été directement affecté par le changement climatique.",
    "15. Votre enfant connaît quelqu'un qui a été directement affecté par le changement climatique.",
    "16. Votre enfant a constaté l'altération d'un lieu important pour lui à la suite du changement climatique.",
    "17. Votre enfant aurait aimé se comporter d'une façon plus respectueuse de l'environnement.",
    "18. Votre enfant recycle.",
    "19. Votre enfant éteint les lumières.",
    "20. Votre enfant essaie de réduire les comportements qui contribuent au changement climatique.",
    "21. Votre enfant se sent coupable s'il gaspille de l'énergie.",
    "22. Votre enfant croit qu'il peut faire quelque chose pour aider à faire face au changement climatique.",
]


def identification_block() -> dict[str, Any]:
    intro = (
        "Commencez par les informations concernant l'enfant ou l'adolescent. "
        "Toutes les réponses sont nécessaires pour valider cette première section."
    )
    return block(
        "Identification et informations générales",
        [
            open_text("ident_nom", "Nom de l'enfant", subheader=intro),
            open_text("ident_prenom", "Prénom de l'enfant"),
            single_choice(
                "ident_genre",
                "Avec quel genre votre enfant souhaite-t-il se définir ?",
                ["Masculin", "Féminin", "Autre"],
            ),
            date_question("ident_naissance", "Date de naissance de l'enfant"),
            open_text("ident_taille", "Taille de l'enfant en centimètres", input_type="number"),
            open_text("ident_poids", "Poids de l'enfant en kilogrammes", input_type="number"),
            open_text("ident_ville", "Ville de résidence de l'enfant"),
            open_text(
                "ident_antecedents_familiaux",
                "Existe-t-il des pathologies notables dans la famille ?",
                long_answer=True,
                placeholder="Décrivez brièvement les antécédents familiaux.",
            ),
            open_text(
                "ident_antecedents_enfant",
                "Votre enfant a-t-il des antécédents notables concernant sa scolarité, son développement, l'acquisition de la marche, du langage ou de la propreté, ou concernant un trouble psychologique, psychiatrique ou médical ?",
                long_answer=True,
            ),
            open_text(
                "ident_ecrans_semaine",
                "Combien d'heures par jour votre enfant passe-t-il en moyenne devant les écrans pendant la semaine d'école ?",
                input_type="number",
            ),
            open_text(
                "ident_ecrans_weekend",
                "Combien d'heures par jour votre enfant passe-t-il en moyenne devant les écrans le week-end ou pendant les vacances ?",
                input_type="number",
            ),
            open_text(
                "ident_prise_en_charge",
                "Votre enfant bénéficie-t-il de prises en charge en orthophonie, psychomotricité, ergothérapie, psychologie ou psychiatrie ?",
                long_answer=True,
            ),
            open_text(
                "ident_traitements",
                "Votre enfant prend-il actuellement des traitements médicamenteux ?",
                long_answer=True,
            ),
        ],
    )


def build_blocks() -> list[dict[str, Any]]:
    conners_intro = (
        "Pensez au comportement habituel de votre enfant au cours des six derniers mois. "
        "Sélectionnez une réponse pour chaque ligne."
    )
    snap_intro = (
        "Basez-vous sur ce que vous avez observé au cours des six derniers mois. "
        "Toutes les lignes doivent recevoir une réponse."
    )
    sleep_intro = (
        "Basez-vous sur les six derniers mois. Pour la fréquence : rarement signifie 1 à 3 fois "
        "par mois, parfois 1 à 2 fois par semaine, souvent 3 à 5 fois par semaine et toujours tous les jours."
    )
    srs_intro = (
        "Pour chaque comportement, choisissez la réponse qui décrit le mieux votre enfant. "
        "Utilisez « Ne s'applique pas » lorsqu'un item ne peut réellement pas être évalué."
    )
    scq_intro = (
        "Certaines questions regroupent plusieurs comportements. Répondez « Oui » si au moins l'un d'eux "
        "a été présent à une période de la vie de votre enfant."
    )
    camouflage_intro = (
        "Ces comportements peuvent être discrets et ce questionnaire peut sembler moins adapté à certains enfants. "
        "Répondez selon ce que vous observez le plus souvent."
    )
    eco_intro = (
        "Ce thème peut sembler différent des autres. Il aide à repérer d'éventuelles préoccupations liées "
        "au changement climatique chez votre enfant."
    )

    blocks: list[dict[str, Any]] = [identification_block()]
    blocks.append(
        block(
            "Questionnaire abrégé de Conners",
            [matrix("conners", "Questionnaire abrégé de Conners", CONNERS, ["Pas du tout", "Un petit peu", "Beaucoup", "Énormément"], subheader=conners_intro)],
        )
    )
    for part, rows in enumerate((SNAP_IV[:13], SNAP_IV[13:]), start=1):
        blocks.append(
            block(
                f"Échelle de TDAH SNAP-IV - partie {part}/2",
                [
                    matrix(
                        f"snap_{part}",
                        f"Échelle de TDAH SNAP-IV - partie {part}/2",
                        rows,
                        ["Pas du tout", "Un peu", "Souvent", "Très souvent"],
                        subheader=snap_intro if part == 1 else "Poursuivez avec les items suivants.",
                    )
                ],
            )
        )
    blocks.append(
        block(
            "Dépistage des troubles du sommeil - partie 1/2",
            [
                single_choice(
                    "sleep_hours",
                    "1. Combien d'heures votre enfant dort-il la plupart des nuits ?",
                    ["Plus de 9 h", "8 à 9 h", "7 à 8 h", "5 à 7 h", "Moins de 5 h"],
                    subheader=sleep_intro,
                ),
                single_choice(
                    "sleep_latency",
                    "2. Combien de temps après sa mise au lit votre enfant met-il habituellement pour s'endormir ?",
                    ["Moins de 15 min", "15 à 30 min", "30 à 45 min", "45 à 60 min", "Plus de 60 min"],
                ),
                matrix("sleep_1", "Sommeil - items 3 à 13", SLEEP_ITEMS[:11], SLEEP_FREQUENCY),
            ],
        )
    )
    blocks.append(
        block(
            "Dépistage des troubles du sommeil - partie 2/2",
            [matrix("sleep_2", "Sommeil - items 14 à 25", SLEEP_ITEMS[11:], SLEEP_FREQUENCY, subheader="Poursuivez en utilisant le même barème de fréquence.")],
        )
    )
    blocks.append(
        block(
            "Échelle d'Epworth",
            [
                matrix(
                    "epworth",
                    "Échelle d'Epworth pour la somnolence diurne",
                    EPWORTH,
                    ["Risque inexistant", "Risque minime", "Risque modéré", "Risque important"],
                    subheader="Au cours des 30 derniers jours, estimez le risque que votre enfant s'endorme dans chaque situation. Si une activité n'a pas eu lieu, imaginez l'effet probable.",
                )
            ],
        )
    )
    blocks.append(
        block(
            "Index de sévérité de l'insomnie",
            [
                single_choice(
                    "isi_1",
                    "1. Quelle est la sévérité actuelle des difficultés de votre enfant à s'endormir ?",
                    ["Aucune", "Légère", "Moyenne", "Importante", "Extrême"],
                    subheader="À partir de ce que vous observez, estimez les difficultés de sommeil de votre enfant au cours du dernier mois.",
                ),
                single_choice("isi_2", "2. Quelle est la sévérité de ses réveils nocturnes fréquents ou prolongés ?", ["Aucune", "Légère", "Moyenne", "Importante", "Extrême"]),
                single_choice("isi_3", "3. Quelle est la sévérité de ses réveils trop précoces le matin ?", ["Aucune", "Légère", "Moyenne", "Importante", "Extrême"]),
                single_choice("isi_4", "4. Jusqu'à quel point votre enfant est-il satisfait de son sommeil actuel ?", ["Très satisfait", "Satisfait", "Plutôt satisfait", "Insatisfait", "Très insatisfait"]),
                single_choice("isi_5", "5. Jusqu'à quel point ses difficultés de sommeil perturbent-elles son fonctionnement quotidien, par exemple la fatigue, la concentration, la mémoire ou l'humeur ?", ["Aucunement", "Légèrement", "Moyennement", "Beaucoup", "Extrêmement"]),
                single_choice("isi_6", "6. À quel point ses difficultés de sommeil sont-elles remarquées par les autres en raison de leurs effets sur sa qualité de vie ?", ["Aucunement", "Légèrement", "Moyennement", "Très", "Extrêmement"]),
                single_choice("isi_7", "7. Jusqu'à quel point votre enfant est-il préoccupé par ses difficultés de sommeil ?", ["Aucunement", "Légèrement", "Moyennement", "Très", "Extrêmement"]),
            ],
        )
    )
    had_intro = (
        "Pensez à ce que votre enfant a semblé ressentir au cours de la semaine écoulée. "
        "Choisissez la réponse qui correspond le mieux à votre observation."
    )
    for part, items in enumerate((HAD[:7], HAD[7:]), start=1):
        elements = [
            single_choice(
                f"had_{index}",
                headline,
                labels,
                subheader=had_intro if part == 1 and position == 0 else None,
            )
            for position, (index, (headline, labels)) in enumerate(
                zip(range(1 if part == 1 else 8, 8 if part == 1 else 15), items)
            )
        ]
        blocks.append(block(f"Échelle HAD - partie {part}/2", elements))
    srs_columns = ["Pas vrai", "Parfois vrai", "Souvent vrai", "Presque toujours vrai", "Ne s'applique pas"]
    for part, rows in enumerate((SRS[:22], SRS[22:44], SRS[44:]), start=1):
        blocks.append(
            block(
                f"Échelle de réciprocité sociale SRS - partie {part}/3",
                [matrix(f"srs_{part}", f"Échelle SRS - partie {part}/3", rows, srs_columns, subheader=srs_intro if part == 1 else "Poursuivez avec les comportements suivants.")],
            )
        )
    for part, rows in enumerate((SCQ[:20], SCQ[20:]), start=1):
        blocks.append(
            block(
                f"Questionnaire sur la communication sociale SCQ - partie {part}/2",
                [matrix(f"scq_{part}", f"Questionnaire SCQ - partie {part}/2", rows, ["Oui", "Non"], subheader=scq_intro if part == 1 else "Pour cette partie, pensez à la période entre le 4e et le 5e anniversaire de votre enfant.")],
            )
        )
    agreement = ["Pas du tout d'accord", "Pas d'accord", "Plutôt pas d'accord", "Ni d'accord ni pas d'accord", "Plutôt d'accord", "D'accord", "Complètement d'accord"]
    for part, rows in enumerate((CAMOUFLAGE[:13], CAMOUFLAGE[13:]), start=1):
        blocks.append(
            block(
                f"Questionnaire du camouflage - partie {part}/2",
                [matrix(f"camouflage_{part}", f"Questionnaire du camouflage - partie {part}/2", rows, agreement, subheader=camouflage_intro if part == 1 else "Poursuivez avec les affirmations suivantes.")],
            )
        )
    for part, rows in enumerate((ECO_ANXIETY[:13], ECO_ANXIETY[13:]), start=1):
        blocks.append(
            block(
                f"Échelle d'éco-anxiété - partie {part}/2",
                [matrix(f"eco_{part}", f"Échelle d'éco-anxiété - partie {part}/2", rows, ["Jamais", "Rarement", "Parfois", "Souvent", "Presque toujours"], subheader=eco_intro if part == 1 else "Dernière partie : merci pour votre attention jusqu'ici.")],
                final=part == 2,
            )
        )
    return blocks


def build_payload(workspace_id: str, *, publish: bool = False) -> dict[str, Any]:
    return {
        "workspaceId": workspace_id,
        "name": "myHCL TND - questionnaire parent",
        "type": "link",
        "status": "inProgress" if publish else "draft",
        "metadata": {
            "title": tr("myHCL TND - questionnaire parent"),
            "description": tr("Questionnaires sur le neurodéveloppement, renseignés par un parent au sujet de son enfant."),
        },
        "defaultLanguage": LANGUAGE,
        "languages": [{"code": LANGUAGE, "default": True, "enabled": True}],
        "welcomeCard": {
            "enabled": True,
            "headline": tr("Questionnaire myHCL TND"),
            "subheader": tr(
                "Merci de prendre ce temps pour votre enfant. Avancez à votre rythme : chaque section validée est enregistrée avant de passer à la suivante. Vous pouvez faire une pause entre deux sections et reprendre avec le même lien et le même navigateur pendant 24 heures. Ce recueil ne fournit pas de diagnostic et ne remplace pas l'évaluation d'un professionnel."
            ),
            "buttonLabel": tr("Commencer"),
            "timeToFinish": False,
            "showResponseCount": False,
        },
        "blocks": build_blocks(),
        "endings": [
            {
                "id": stable_cuid("myhcl-tnd-ending"),
                "type": "endScreen",
                "headline": tr("Merci, le questionnaire est terminé"),
                "subheader": tr("Vos réponses ont bien été enregistrées. Merci pour votre temps et votre attention."),
            }
        ],
        "hiddenFields": {"enabled": True, "fieldIds": ["participant_id"]},
        "variables": [],
    }


def logical_question_count(payload: dict[str, Any]) -> int:
    count = 0
    for survey_block in payload["blocks"]:
        for element in survey_block["elements"]:
            count += len(element["rows"]) if element["type"] == "matrix" else 1
    return count

