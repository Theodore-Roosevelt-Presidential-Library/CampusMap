"""Builds interior.json for the CampusMap repo: interior stops (galleries 1-28, narrative A-D,
public spaces) and visitor-information markers, positioned on the campus model.

Positions come from the published exhibit map (trlibrary.com/visit/maps), registered to the
architects' floor plans (A201/A202, conformed set) and from there to the campus model."""
import json
from classify import web2ft
from common import ft2cm

EX = 'https://www.trlibrary.com/visit/exhibits/main#gallery-'
def cta(anchor, label='Read about this gallery'):
    return {'label': label, 'url': EX + anchor}

# (number/letter, id, title, web px, description, image id or None, exhibits anchor)
GALLERIES = [
 ('1', 'call-to-adventure', 'A Call to Adventure', (710, 699),
  "The journey starts on a New York City sidewalk outside the brownstone where Theodore Roosevelt was born. Meet him as a small, asthmatic boy who traveled the world through books, while the stories he read play out in the windows above.",
  'call-to-adventure', 'call-to-adventure'),
 ('2', 'parlor', 'Roosevelt Family Parlor', (659, 701),
  "Step into the warm hush of a Victorian parlor, the room where young Theodore's character took shape. Meet the parents who gave him a sense of duty and a sense of wonder, and look for the family Bible given to his father by the newsboys he helped.",
  'parlor', 'parlor'),
 ('3', 'museum-of-natural-history', 'Roosevelt Museum of Natural History', (567, 687),
  "At nine, Theodore turned his bedroom into a natural history museum. This gallery reimagines it as part bedroom, part daydream. Use your Trailblazer Compass to find animals hidden among the specimens and watch them spring to life.",
  'museum-of-natural-history', 'museum-of-natural-history'),
 ('4', 'memory-train', 'Memory Train', (328, 726),
  "Ride a train car through the happiest years of Roosevelt's young life: his courtship of Alice Hathaway Lee, their marriage and his first election. Lean in close to the wallpaper and you'll find fragments of real love letters.",
  'memory-train', 'memory-train'),
 ('5', 'loss', 'Loss', (232, 693),
  "On February 14, 1884, Roosevelt lost his wife and his mother within hours of each other. His diary is here, open to the page where he marked that day with a heavy black X. Stand with it a moment, then follow him west to the Badlands.",
  'loss', 'loss'),
 ('6', 'elkhorn-ranch', 'Elkhorn Ranch', (232, 528),
  "In the Dakota Badlands, a grieving young man rebuilt his life and began his evolution into a conservationist. See his buckskin hunting outfit, his Tiffany hunting knife and branding irons from the Maltese Cross and Elkhorn ranches, and watch the conservation film at the heart of the gallery.",
  'elkhorn-ranch', 'elkhorn-ranch'),
 ('7', 'storytelling-campfire', 'Storytelling Campfire', (306, 528),
  "Pull up a rocking chair by a nighttime campfire in Medora. Roosevelt's real Badlands companions, including Joe Ferris, Bill Sewall and Bill Merrifield, swap stories of their adventures on the northern plains.",
  'storytelling-campfire', 'storytelling-campfire'),
 ('8', 'ranch-activities', 'Ranch Activities', (336, 675),
  "Now try your hand at ranch life. Test your aim at target practice, design your own cattle brand, join the roundup and step up to deliver part of one of Roosevelt's early speeches.",
  'ranch-activities', 'ranch-activities'),
 ('9', 'assembling-the-rough-riders', 'Assembling the Rough Riders', (554, 499),
  "When war broke out in 1898, Roosevelt resigned as Assistant Secretary of the Navy to fight. He helped raise a volunteer cavalry regiment that brought cowboys and ranch hands together with Ivy League athletes, lawmen and frontiersmen. The press called them the Rough Riders.",
  None, 'setup-for-war'),
 ('10', 'pre-battle-camp', 'Pre-Battle Camp', (569, 576),
  "Step into Roosevelt's tent on the eve of battle. Inside is the Rough Riders uniform Brooks Brothers tailored for him, shown with his sword, campaign hat and spurs, along with a watercolor painted in the encampment.",
  'pre-battle-camp', 'setup-for-war'),
 ('11', 'san-juan-heights', 'Battle of San Juan Heights', (652, 576),
  "In this immersive theater, the July 1898 assault on the San Juan Heights unfolds around you through the voices of the men who were there. Roosevelt leads from the front, and a colonel of volunteers becomes a national figure overnight.",
  'san-juan-heights', 'san-juan-heights'),
 ('12', 'post-battle', 'Post-Battle Outcomes', (659, 504),
  "Roosevelt came home from Cuba a celebrity, and his Rough Riders became a sensation. A case full of Rough Rider games, sheet music and souvenirs shows that fame at work. Pose for a photo with the regiment at the top of the hill.",
  'post-battle', 'post-battle'),
 ('13', 'path-to-the-presidency', 'Path to the Presidency', (675, 422),
  "In barely three years, Roosevelt went from war hero to Governor of New York to vice president. Walk the campaign hall, and look for his \"TR for Governor\" ribbons and his 1899 speech \"The Strenuous Life.\"",
  'path-to-the-presidency', 'governorship'),
 ('14', 'vice-presidency', 'Vice Presidency', (678, 255),
  "In 1900, Roosevelt crossed the country on a whistle-stop tour as William McKinley's running mate. Browse the campaign memorabilia, then build your own campaign poster and add it to the growing wall of candidates.",
  'vice-presidency', 'vice-presidency'),
 ('15', 'white-house-facade', 'White House Facade', (567, 357),
  "A full-scale White House facade opens Roosevelt's presidency. A film narrated by Nick Offerman covers the eight years that remade the office, from the Square Deal to the Panama Canal and the Nobel Peace Prize.",
  'white-house-facade', 'white-house-facade'),
 ('16', 'conservation-bronze', 'Conservation Bronze', (501, 378),
  "A stop dedicated to Roosevelt's conservation record. As president he protected roughly 230 million acres of public land, including national forests, bird reserves, national monuments and national parks.",
  None, 'modern-presidency'),
 ('17', 'roosevelts-white-house', "Roosevelt's White House", (375, 359),
  "Meet the man inside the office. Photographs and personal objects from his presidential years fill the cases, including a ring holding a lock of Abraham Lincoln's hair. Then step into the role yourself: make the hard calls in Run Your Own Presidency and pose for your own presidential portrait.",
  'roosevelts-white-house', 'trs-white-house'),
 ('18', 'talk-with-tr', 'Talk with TR', (303, 359),
  "Ask Theodore Roosevelt a question out loud, and a life-size, conversational TR answers with responses drawn from what he actually wrote and said. The Lincoln portrait he kept in his own White House office hangs nearby.",
  'talk-with-tr', 'talk-with-the-president'),
 ('19', 'white-house-gang', 'White House Gang', (222, 421),
  "Roosevelt's children and their friends turned the executive mansion into a playground. Led by young Quentin, the White House Gang roller-skated through the halls and once smuggled a pony into the elevator. This gallery is a space to play.",
  'white-house-gang', 'white-house-gang'),
 ('20', 'family-room', 'Roosevelt Family Room', (212, 275),
  "With six children and a menagerie of pets, the White House became one of the liveliest family homes it has ever been. Meet Edith Roosevelt, who reshaped the role of First Lady, and Alice, the celebrity of her era.",
  'family-room', 'white-house-family-room'),
 ('21', 'east-africa', 'East Africa', (364, 210),
  "The day after leaving the White House, Roosevelt set off on a scientific expedition to Africa for the Smithsonian. The specimens on display came from that expedition and still carry their original field tags, signed in Roosevelt's own hand.",
  'east-africa', 'african-expedition'),
 ('22', 'in-the-arena', 'In the Arena', (258, 169),
  "Roosevelt's most famous passage lights up line by line around a great circular sculpture as it is read aloud. The voices rotate through the day and include presidents, first ladies, historians, artists and a Roosevelt descendant. Then make your own pledge.",
  'in-the-arena', 'in-the-arena'),
 ('23', 'bull-moose', 'Bull Moose Campaign', (331, 144),
  "In 1912, Roosevelt was shot in the chest on his way to a campaign speech, and he gave the speech anyway. See the eyeglasses case and the folded speech that slowed the bullet. Then cast a ballot on the issues of 1912 in a period voting booth.",
  'bull-moose', 'bull-moose-campaign'),
 ('24', 'the-amazon', 'The Amazon', (534, 137),
  "An immersive film puts you in the boats with Roosevelt and his son Kermit as they trace the uncharted River of Doubt. It is the expedition that nearly killed him. Brazil later renamed the river the Rio Roosevelt.",
  None, 'the-amazon'),
 ('25', 'sagamore-hill', 'Sagamore Hill', (539, 210),
  "Step into the warm, crowded rooms of Roosevelt's beloved Long Island home, full of a lifetime of collecting. Look for the famous rhinoceros-foot inkwell, a souvenir of Africa he kept on his desk.",
  'sagamore-hill', 'sagamore-hill'),
 ('26', 'january-6-1919', 'January 6, 1919', (626, 199),
  "Theodore Roosevelt died in his sleep at Sagamore Hill on January 6, 1919, at the age of sixty. This quiet stop marks the end of a restless life.",
  None, 'sagamore-hill'),
 ('27', 'legacy', 'Legacy', (655, 142),
  "Each ring in a plank of copper beech from Sagamore Hill counts a year of American history. Nearby are two original Medals of Honor, earned by Theodore Roosevelt and his son Theodore Roosevelt Jr.",
  'legacy', 'legacy'),
 ('28', 'peoples-library', "The People's Library", (831, 139),
  "The final room looks out on Theodore Roosevelt National Park. Tap your Trailblazer Compass one last time to reveal your own constellation, a map of the choices you made along the way.",
  'peoples-library', 'legacy'),
]
NARRATIVE = [
 ('A', 'young-adulthood', 'Young Adulthood', (460, 723),
  "The first Narrative Gallery covers the decade that made the man: Harvard, the death of his father, his first book and his first seat in the New York State Assembly. His Harvard record and marriage certificate are among the objects on view.",
  'young-adulthood', 'young-adulthood'),
 ('B', 'political-education', 'Political Education', (460, 603),
  "Back from the Badlands, Roosevelt became one of the most fearless reformers in American government, first as a U.S. Civil Service Commissioner and then as New York City's police commissioner. A police helmet and badge from the force he remade are on view.",
  'political-education', 'political-rise'),
 ('C', 'modern-presidency', 'Modern Presidency', (460, 413),
  "In seven years, Roosevelt remade the presidency: the Square Deal, trust-busting, the 1902 coal strike settlement and roughly 230 million acres of protected public land. The gallery also takes an honest look at the contradictions in his record on race.",
  'modern-presidency', 'modern-presidency'),
 ('D', 'final-years', 'Final Years', (460, 174),
  "After the presidency, Roosevelt never slowed down. He championed women's suffrage, argued for preparedness in the World War and saw all four of his sons go to serve. His youngest, Quentin, was killed in France in 1918.",
  None, 'final-years'),
]
SPACES = [
 ('main-lobby', 'Main Lobby', (1010, 448), 1,
  "The front door to the Library, with tickets and admissions. Wheelchairs are available on request here.",
  {'label': 'Buy tickets', 'url': 'https://www.trlibrary.com/tickets'}),
 ('orientation', 'Orientation', (823, 727), 1,
  "The permanent exhibition starts here. Pick up your Trailblazer Compass, a wearable band that unlocks the interactives as you move through eight chapters of Roosevelt's life.",
  {'label': 'Plan your visit', 'url': 'https://www.trlibrary.com/visit/exhibits/main'}),
 ('exhibit-event-gallery', 'Exhibit & Event Gallery', (810, 472), 1,
  "A flexible gallery off the Main Lobby for temporary exhibitions and events.",
  {'label': 'See current exhibits', 'url': 'https://www.trlibrary.com/visit/exhibits'}),
 ('museum-store', 'Museum Store', (1032, 279), 1,
  "Books on Roosevelt and conservation, Library-exclusive merchandise, family-friendly gifts and goods from regional artisans.",
  {'label': 'Shop online', 'url': 'https://shop.trlibrary.com'}),
 ('salt-scoria', 'Salt+Scoria Restaurant', (911, 930), 1,
  "The Library's restaurant, with indoor seating and a terrace looking out over the Badlands.",
  {'label': 'Where to eat', 'url': 'https://www.trlibrary.com/visit/eat'}),
 ('lockers', 'Lockers', (920, 777), 1,
  "Lockers for coats and bags, next to the restrooms off the Main Lobby.", None),
 ('auditorium', 'Auditorium', (1402, 397), 1,
  "The East Wing's auditorium hosts lectures, films and community gatherings, and can be booked for private events.",
  {'label': 'Host an event', 'url': 'https://www.trlibrary.com/private-events'}),
 ('east-wing-lobby', 'East Wing Lobby', (1337, 581), 1,
  "Gathering space for the auditorium and classrooms, with coat check, restrooms and the elevator to the upper floor.", None),
 ('north-classroom', 'North Classroom', (1283, 716), 1,
  "One of two classrooms for school groups, workshops and meetings.",
  {'label': 'For educators', 'url': 'https://www.trlibrary.com/tr/for-educators'}),
 ('south-classroom', 'South Classroom', (1284, 800), 1,
  "One of two classrooms for school groups, workshops and meetings.",
  {'label': 'For educators', 'url': 'https://www.trlibrary.com/tr/for-educators'}),
]
# Upper floor (feet, model frame)
SPACES_L2 = [
 ('board-room', 'Executive Board Room', (344, 11), 2,
  "The upper-floor board room in the East Wing, available for meetings and private events.",
  {'label': 'Host an event', 'url': 'https://www.trlibrary.com/private-events'}),
 ('upper-reception', 'Upper Floor Reception', (333, 94), 2,
  "Arrival area at the top of the East Wing elevator and stairs.", None),
]
# visitor information markers: kind, web px, level, label
AMENITIES = [
 ('restroom', (298, 417), 1, 'Restrooms'), ('restroom', (822, 833), 1, 'Restrooms'), ('restroom', (1478, 690), 1, 'Restrooms'),
 ('family', (911, 855), 1, 'Family restroom'), ('family', (1395, 725), 1, 'Family restroom'),
 ('wheelchair', (982, 603), 1, 'Wheelchairs available on request'),
 ('access', (1270, 413), 1, 'Accessible seating'), ('access', (1350, 519), 1, 'Accessible seating'),
 ('elevator', (1325, 508), 1, 'Elevator to upper floor'),
 ('stairs', (1268, 513), 1, 'Stairs'), ('stairs', (1440, 555), 1, 'Stairs'),
 ('tickets', (980, 572), 1, 'Tickets and admissions'),
 ('coat', (1393, 632), 1, 'Coat check'),
 ('warning', (611, 146), 1, 'Contains flashing, strobing or high-contrast light'),
 ('warning', (692, 624), 1, 'Contains flashing, strobing or high-contrast light'),
 ('exit', (495, 210), 1, 'Early exit to the lobby'),
 ('entrance', (1135, 722), 1, 'West Wing entrance and exit'),
 ('entrance', (1155, 580), 1, 'East Wing entrance and exit'),
]
AMENITIES_L2 = [('elevator', (352, 99), 2, 'Elevator'), ('stairs', (341.5, 66.5), 2, 'Stairs')]
LAYER = {'restroom': 'amenities', 'family': 'amenities', 'coat': 'amenities', 'tickets': 'amenities', 'entrance': 'amenities',
         'exit': 'route', 'wheelchair': 'access', 'access': 'access', 'elevator': 'access', 'stairs': 'access', 'warning': 'warnings'}

def pos_web(px, h=1.0):
    fx, fy = web2ft(*px); X, Y, Z = ft2cm(fx, fy, h); return f'{float(X):.3f} {float(Y):.3f} {float(Z):.3f}'
def pos_ft(f, h):
    X, Y, Z = ft2cm(f[0], f[1], h); return f'{float(X):.3f} {float(Y):.3f} {float(Z):.3f}'

stops = []
for lab, sid, title, px, desc, img, anchor in GALLERIES + NARRATIVE:
    stops.append({'id': sid, 'label': lab, 'kind': 'narrative' if lab.isalpha() else 'gallery', 'level': 1,
                  'title': title, 'image': f'img/poi/inside/{img}.jpg' if img else '', 'description': desc,
                  'cta': cta(anchor), 'position': pos_web(px)})
for sid, title, px, lvl, desc, c in SPACES:
    stops.append({'id': sid, 'label': '', 'kind': 'space', 'level': lvl, 'title': title, 'image': '',
                  'description': desc, 'cta': c, 'position': pos_web(px)})
for sid, title, f, lvl, desc, c in SPACES_L2:
    stops.append({'id': sid, 'label': '', 'kind': 'space', 'level': lvl, 'title': title, 'image': '',
                  'description': desc, 'cta': c, 'position': pos_ft(f, 17)})
amen = [{'kind': k, 'layer': LAYER[k], 'level': lvl, 'label': lab, 'position': pos_web(px)} for k, px, lvl, lab in AMENITIES]
amen += [{'kind': k, 'layer': LAYER[k], 'level': lvl, 'label': lab, 'position': pos_ft(f, 17)} for k, f, lvl, lab in AMENITIES_L2]
out = {'_comment': "Inside the Library: interior stops and visitor-information markers for the campus map's Step Inside mode. "
       "Gallery numbering, names and route follow the exhibit map at trlibrary.com/visit/maps; descriptions are condensed from "
       "trlibrary.com/visit/exhibits/main. level 1 = main floor, 2 = East Wing upper floor. Positions are 'x y z' on the campus model "
       "(add ?edit&inside to the viewer URL and right-click to grab new ones).",
       'stops': stops, 'markers': amen}
json.dump(out, open('/home/claude/campusmap/interior.json', 'w'), indent=2, ensure_ascii=False)
print(len(stops), len(amen))
