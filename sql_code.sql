-- =====================================================
-- NEWS INVESTIGATION DATABASE — COMPLETE CLEAN SQL
-- Run order: Drop → Create DB → Tables → Data →
--            Triggers → Procedures → Views → Queries
-- =====================================================

-- =====================================================
-- STEP 1: SELECT DATABASE
-- =====================================================
CREATE DATABASE IF NOT EXISTS news_investigation_db;
USE news_investigation_db;

-- =====================================================
-- STEP 2: DROP EVERYTHING CLEANLY
-- =====================================================
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS story_audit;
DROP TABLE IF EXISTS source_connection;
DROP TABLE IF EXISTS story_location;
DROP TABLE IF EXISTS Audit_Log;
DROP TABLE IF EXISTS Timeline_Event;
DROP TABLE IF EXISTS Note;
DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS Document;
DROP TABLE IF EXISTS Interview;
DROP TABLE IF EXISTS Source;
DROP TABLE IF EXISTS Story;
DROP TABLE IF EXISTS Users;

DROP VIEW IF EXISTS v_source_overview;
DROP VIEW IF EXISTS v_story_overview;
DROP VIEW IF EXISTS v_location_story;
DROP VIEW IF EXISTS v_interview_details;
DROP VIEW IF EXISTS v_document_details;
DROP VIEW IF EXISTS v_timeline_details;
DROP VIEW IF EXISTS v_city_hotspot;
DROP VIEW IF EXISTS v_most_active_sources;
DROP VIEW IF EXISTS v_incomplete_stories;
DROP VIEW IF EXISTS v_risky_source_story;
DROP VIEW IF EXISTS v_user_roles;
DROP VIEW IF EXISTS v_audit_trail;

DROP PROCEDURE IF EXISTS sp_transfer_interviews;
DROP PROCEDURE IF EXISTS sp_complete_story;
DROP PROCEDURE IF EXISTS sp_upgrade_credibility;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================
-- STEP 3: CREATE TABLES
-- =====================================================

-- Users (login + role system)
CREATE TABLE Users (
    User_ID    INT AUTO_INCREMENT PRIMARY KEY,
    Username   VARCHAR(100) NOT NULL UNIQUE,
    Password   VARCHAR(255) NOT NULL,
    Role       ENUM('Admin','Journalist','Viewer') NOT NULL,
    Full_Name  VARCHAR(255),
    Created_At DATE DEFAULT (CURDATE())
);

-- Audit_Log
CREATE TABLE Audit_Log (
    Log_ID      INT AUTO_INCREMENT PRIMARY KEY,
    Table_Name  VARCHAR(100)  NOT NULL,
    Operation   ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    Record_ID   INT           NOT NULL,
    Changed_By  VARCHAR(100)  DEFAULT 'system',
    Change_Time DATETIME      DEFAULT CURRENT_TIMESTAMP,
    Old_Value   TEXT,
    New_Value   TEXT
);

-- Story
CREATE TABLE Story (
    Story_ID    INT AUTO_INCREMENT PRIMARY KEY,
    Title       VARCHAR(255) NOT NULL,
    Description TEXT,
    Category    VARCHAR(100),
    Start_Date  DATE,
    Status      VARCHAR(50)  CHECK (Status IN ('Ongoing','Completed'))
);

-- Source
CREATE TABLE Source (
    Source_ID         INT AUTO_INCREMENT PRIMARY KEY,
    Name              VARCHAR(255) NOT NULL,
    Type              ENUM('Person','Organization') NOT NULL,
    Contact_Info      VARCHAR(255),
    Credibility_Level INT NOT NULL CHECK (Credibility_Level IN (1,2,3))
);

-- Interview
CREATE TABLE Interview (
    Interview_ID   INT AUTO_INCREMENT PRIMARY KEY,
    Interview_Date DATE,
    Mode           ENUM('Online','In-person') NOT NULL,
    Transcript     TEXT,
    Story_ID       INT NOT NULL,
    Source_ID      INT NOT NULL,
    FOREIGN KEY (Story_ID)  REFERENCES Story(Story_ID)  ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Source_ID) REFERENCES Source(Source_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Document
CREATE TABLE Document (
    Document_ID INT AUTO_INCREMENT PRIMARY KEY,
    Title       VARCHAR(255) NOT NULL,
    Type        VARCHAR(100),
    Upload_Date DATE,
    Story_ID    INT NOT NULL,
    FOREIGN KEY (Story_ID) REFERENCES Story(Story_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Location
CREATE TABLE Location (
    Location_ID INT AUTO_INCREMENT PRIMARY KEY,
    Place_Name  VARCHAR(255),
    City        VARCHAR(100),
    State       VARCHAR(100),
    Country     VARCHAR(100),
    Story_ID    INT NOT NULL,
    FOREIGN KEY (Story_ID) REFERENCES Story(Story_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Note
CREATE TABLE Note (
    Note_ID      INT AUTO_INCREMENT PRIMARY KEY,
    Content      TEXT NOT NULL,
    Created_Date DATE,
    Story_ID     INT NOT NULL,
    FOREIGN KEY (Story_ID) REFERENCES Story(Story_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Timeline_Event
CREATE TABLE Timeline_Event (
    Event_ID    INT AUTO_INCREMENT PRIMARY KEY,
    Event_Title VARCHAR(255),
    Event_Date  DATE,
    Description TEXT,
    Story_ID    INT NOT NULL,
    FOREIGN KEY (Story_ID) REFERENCES Story(Story_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- =====================================================
-- STEP 4: INSERT DATA
-- =====================================================

-- Users
INSERT INTO Users (Username, Password, Role, Full_Name) VALUES
('admin',      SHA2('admin123',      256), 'Admin',      'Admin User'),
('journalist', SHA2('journalist123', 256), 'Journalist', 'Jane Reporter'),
('viewer',     SHA2('viewer123',     256), 'Viewer',     'Editor Evans');

-- Stories (40)
INSERT INTO Story (Title, Description, Category, Start_Date, Status) VALUES
('City Corruption Case',         'Misuse of public funds by officials',       'Politics',    '2025-01-01', 'Ongoing'),
('Tech Startup Fraud',           'Financial fraud in startup',                'Business',    '2025-02-10', 'Completed'),
('Environmental Violation',      'Illegal industrial dumping',                'Environment', '2025-03-01', 'Ongoing'),
('Healthcare Scam',              'Insurance claim manipulation',              'Health',      '2025-03-15', 'Ongoing'),
('Real Estate Laundering',       'Property laundering scheme',                'Crime',       '2025-04-01', 'Ongoing'),
('Education Grant Misuse',       'Misuse of public education grants',         'Education',   '2025-04-10', 'Ongoing'),
('Police Bribery Ring',          'Officers taking bribes from criminals',     'Crime',       '2025-01-15', 'Ongoing'),
('Hospital Drug Scam',           'Fake medicines sold in hospitals',          'Health',      '2025-02-01', 'Completed'),
('Mining Permit Fraud',          'Illegal mining permits issued',             'Politics',    '2025-02-20', 'Ongoing'),
('School Fund Diversion',        'School funds redirected to private use',    'Education',   '2025-03-05', 'Ongoing'),
('Water Supply Corruption',      'Contaminated water covered up',             'Environment', '2025-03-20', 'Ongoing'),
('Bank Loan Fraud',              'Fake loan applications approved',           'Business',    '2025-04-05', 'Completed'),
('Election Rigging Probe',       'Voting machine tampering alleged',          'Politics',    '2025-01-10', 'Ongoing'),
('Food Adulteration Network',    'Poisoned food supply chain exposed',        'Health',      '2025-02-15', 'Ongoing'),
('Land Grabbing Scheme',         'Farmers land illegally acquired',           'Crime',       '2025-03-10', 'Ongoing'),
('Tax Evasion Investigation',    'Corporate tax evasion uncovered',           'Business',    '2025-04-01', 'Completed'),
('Child Labor Exposure',         'Underage workers in factories',             'Crime',       '2025-01-25', 'Ongoing'),
('Pharmaceutical Kickbacks',     'Doctors paid to prescribe drugs',           'Health',      '2025-02-28', 'Ongoing'),
('Infrastructure Scam',          'Bridge construction funds stolen',          'Politics',    '2025-03-25', 'Ongoing'),
('Cyber Fraud Network',          'Large scale online banking fraud',          'Business',    '2025-04-15', 'Ongoing'),
('Arms Smuggling Ring',          'Illegal weapons crossing borders',          'Crime',       '2025-01-05', 'Ongoing'),
('Pension Fund Theft',           'Retirement funds siphoned off',             'Business',    '2025-02-08', 'Ongoing'),
('University Admission Scam',    'Fake admissions for bribes',                'Education',   '2025-03-12', 'Ongoing'),
('Forest Land Encroachment',     'Protected land cleared illegally',          'Environment', '2025-04-08', 'Ongoing'),
('Fuel Subsidy Fraud',           'False subsidy claims filed',                'Politics',    '2025-01-18', 'Ongoing'),
('Refugee Aid Diversion',        'Aid funds not reaching refugees',           'Health',      '2025-02-25', 'Ongoing'),
('Traffic Police Bribery',       'Officers extorting drivers daily',          'Crime',       '2025-03-18', 'Ongoing'),
('Medical Device Fraud',         'Substandard devices approved',              'Health',      '2025-04-12', 'Ongoing'),
('Coal Mining Scandal',          'Illegal coal extraction licensed',          'Environment', '2025-01-22', 'Ongoing'),
('Sports Betting Fix',           'Match fixing with organized crime',         'Crime',       '2025-02-18', 'Ongoing'),
('NGO Fund Misuse',              'Charity funds diverted privately',          'Education',   '2025-03-22', 'Ongoing'),
('Food Import Scandal',          'Contaminated imports allowed',              'Health',      '2025-04-18', 'Ongoing'),
('Border Customs Fraud',         'Goods smuggled through customs',            'Crime',       '2025-01-28', 'Ongoing'),
('Telecom License Scam',         'Licenses issued for bribes',                'Business',    '2025-02-22', 'Ongoing'),
('Urban Planning Corruption',    'Zoning laws violated for profit',           'Politics',    '2025-03-28', 'Ongoing'),
('Social Welfare Fraud',         'Benefits claimed by ghost persons',         'Politics',    '2025-04-22', 'Ongoing'),
('Airport Contract Scam',        'Inflated contracts awarded',                'Business',    '2025-01-30', 'Ongoing'),
('Pesticide Contamination',      'Banned pesticides used on crops',           'Environment', '2025-02-26', 'Ongoing'),
('Prison Corruption Ring',       'Guards enabling criminal activity',         'Crime',       '2025-03-30', 'Ongoing'),
('Defense Procurement Fraud',    'Military equipment overbilled',             'Politics',    '2025-04-25', 'Ongoing');

-- Sources (200: 67 Low + 67 Medium + 66 High)
INSERT INTO Source (Name, Type, Contact_Info, Credibility_Level) VALUES
-- LOW (1)
('Daily Buzz Blog',           'Organization', 'buzz@blog.com',          1),
('Tom Lee',                   'Person',       'tom@email.com',          1),
('Unknown Insider',           'Person',       'unknown@email.com',      1),
('Gossip Weekly',             'Organization', 'gossip@weekly.com',      1),
('Anonymous Tip X',           'Person',       'tipx@email.com',         1),
('Viral Shorts Media',        'Organization', 'viral@shorts.com',       1),
('Unnamed Source A',          'Person',       'sourcea@email.com',      1),
('Clickbait Daily',           'Organization', 'click@daily.com',        1),
('Rumor Mill Blog',           'Organization', 'rumor@mill.com',         1),
('Unverified Voice',          'Person',       'uvvoice@email.com',      1),
('Shadow Informant',          'Person',       'shadow@email.com',       1),
('Fake Report Network',       'Organization', 'fake@report.com',        1),
('Anonymous Source Z',        'Person',       'anonz@email.com',        1),
('Tabloid Express',           'Organization', 'tabloid@express.com',    1),
('Mystery Tipper B',          'Person',       'mysteryb@email.com',     1),
('Unconfirmed Source C',      'Person',       'unconf@email.com',       1),
('Fake News Central',         'Organization', 'fnc@fake.com',           1),
('WhatsApp Forward Guy',      'Person',       'wfg@email.com',          1),
('No Proof Portal',           'Organization', 'npp@portal.com',         1),
('Anonymous Leaker D',        'Person',       'leakerd@email.com',      1),
('Conspiracy Blog',           'Organization', 'conspiracy@blog.com',    1),
('Unnamed Insider E',         'Person',       'insidere@email.com',     1),
('Misinformation Hub',        'Organization', 'misinfo@hub.com',        1),
('Random Tipster F',          'Person',       'tipsterf@email.com',     1),
('Satire Portal',             'Organization', 'satire@portal.com',      1),
('Unverified Blog G',         'Organization', 'unvblog@g.com',          1),
('Secret Source H',           'Person',       'secreth@email.com',      1),
('No Evidence Network',       'Organization', 'noev@network.com',       1),
('Ghost Reporter I',          'Person',       'ghosti@email.com',       1),
('Fake Scoop Daily',          'Organization', 'fakescoop@daily.com',    1),
('Anonymous Caller J',        'Person',       'callerj@email.com',      1),
('Unverified Source K',       'Person',       'sourcek@email.com',      1),
('Junk News Today',           'Organization', 'junk@newstoday.com',     1),
('Mystery Person L',          'Person',       'mysteryl@email.com',     1),
('Fake Alert Media',          'Organization', 'fakealert@media.com',    1),
('Unknown Caller M',          'Person',       'callerm@email.com',      1),
('Clickfarm News',            'Organization', 'clickfarm@news.com',     1),
('Unverified Source N',       'Person',       'sourcen@email.com',      1),
('Bogus Report Blog',         'Organization', 'bogus@report.com',       1),
('Anonymous Person O',        'Person',       'persono@email.com',      1),
('Fake Digest Weekly',        'Organization', 'fakedigest@weekly.com',  1),
('Unnamed Source P',          'Person',       'sourcep@email.com',      1),
('Misinformation Daily',      'Organization', 'misinfo@daily.com',      1),
('Random Person Q',           'Person',       'personq@email.com',      1),
('No Source Portal',          'Organization', 'nosource@portal.com',    1),
('Unknown Tipper R',          'Person',       'tipperr@email.com',      1),
('Unverified Network S',      'Organization', 'networks@unver.com',     1),
('Ghost Source T',            'Person',       'ghostt@email.com',       1),
('Fake Bulletin Board',       'Organization', 'fakebb@board.com',       1),
('Anonymous Source U',        'Person',       'sourceu@email.com',      1),
('Hoax Report Media',         'Organization', 'hoax@reportmedia.com',   1),
('Random Caller V',           'Person',       'callerv@email.com',      1),
('Unverified Portal W',       'Organization', 'portalw@unver.com',      1),
('Mystery Source X',          'Person',       'mysteryx@email.com',     1),
('Spam News Network',         'Organization', 'spam@newsnetwork.com',   1),
('Unnamed Person Y',          'Person',       'persony@email.com',      1),
('Fake Flash News',           'Organization', 'fakeflash@news.com',     1),
('Anonymous Informer Z2',     'Person',       'informerz2@email.com',   1),
('Unconfirmed Blog A2',       'Organization', 'unconfblog@a2.com',      1),
('Ghost Tipper B2',           'Person',       'tipperb2@email.com',     1),
('Misinformation Weekly',     'Organization', 'misinfo@weekly.com',     1),
('Unknown Source C2',         'Person',       'sourcec2@email.com',     1),
('Fake Pulse Media',          'Organization', 'fakepulse@media.com',    1),
('Anonymous Insider D2',      'Person',       'insiderd2@email.com',    1),
('No Verify Network',         'Organization', 'noverify@network.com',   1),
('Random Blogger E2',         'Person',       'bloggere2@email.com',    1),
('Unverified Flash News',     'Organization', 'unverflash@news.com',    1),
('Secret Tipper F2',          'Person',       'tipperf2@email.com',     1),
-- MEDIUM (2)
('Sara Khan',                 'Person',       'sara@email.com',         2),
('Michael Brown',             'Person',       'michael@email.com',      2),
('City Times',                'Organization', 'city@times.com',         2),
('Metro Reporter',            'Organization', 'metro@news.com',         2),
('District Observer',         'Organization', 'district@obs.com',       2),
('James Patel',               'Person',       'james@email.com',        2),
('Regional Pulse',            'Organization', 'regional@pulse.com',     2),
('Neha Sharma',               'Person',       'neha@email.com',         2),
('Weekly Chronicle',          'Organization', 'weekly@chron.com',       2),
('Carlos Rivera',             'Person',       'carlos@email.com',       2),
('Community Herald',          'Organization', 'comm@herald.com',        2),
('Priya Nair',                'Person',       'priya@email.com',        2),
('Town Crier News',           'Organization', 'town@crier.com',         2),
('Ravi Kumar',                'Person',       'ravi@email.com',         2),
('Evening Standard Local',    'Organization', 'evening@standard.com',   2),
('Aisha Patel',               'Person',       'aisha@email.com',        2),
('Suburban News Net',         'Organization', 'suburban@newsnet.com',   2),
('Derek Johnson',             'Person',       'derek@email.com',        2),
('Local Insight Media',       'Organization', 'local@insight.com',      2),
('Fatima Malik',              'Person',       'fatima@email.com',       2),
('Midtown Gazette',           'Organization', 'midtown@gazette.com',    2),
('Samuel Okafor',             'Person',       'samokafor@email.com',    2),
('City Beat Network',         'Organization', 'citybeat@network.com',   2),
('Lena Fischer',              'Person',       'lena@email.com',         2),
('Weekend Tribune',           'Organization', 'weekend@tribune.com',    2),
('Raj Verma',                 'Person',       'raj@email.com',          2),
('Morning Bulletin',          'Organization', 'morning@bulletin.com',   2),
('Amina Hassan',              'Person',       'amina@email.com',        2),
('District Daily',            'Organization', 'district@daily.com',     2),
('Peter Nguyen',              'Person',       'peter@email.com',        2),
('Region Watch Media',        'Organization', 'regionwatch@media.com',  2),
('Sofia Martinez',            'Person',       'sofia@email.com',        2),
('Citizen Press',             'Organization', 'citizen@press.com',      2),
('Ahmed Ali',                 'Person',       'ahmed@email.com',        2),
('Local News Wire',           'Organization', 'local@newswire.com',     2),
('Nina Petrova',              'Person',       'nina@email.com',         2),
('Uptown Observer',           'Organization', 'uptown@observer.com',    2),
('Kwame Mensah',              'Person',       'kwame@email.com',        2),
('Community Pulse',           'Organization', 'community@pulse.com',    2),
('Isabel Torres',             'Person',       'isabel@email.com',       2),
('Neighborhood News',         'Organization', 'neighborhood@news.com',  2),
('Omar Farooq',               'Person',       'omar@email.com',         2),
('Metro Insight',             'Organization', 'metro@insight.com',      2),
('Yuki Tanaka',               'Person',       'yuki@email.com',         2),
('Regional Report',           'Organization', 'regional@report.com',    2),
('Diego Hernandez',           'Person',       'diego@email.com',        2),
('Local Tribune',             'Organization', 'local@tribune.com',      2),
('Mei Lin',                   'Person',       'meilin@email.com',       2),
('City Insight Daily',        'Organization', 'cityinsight@daily.com',  2),
('Arjun Singh',               'Person',       'arjun@email.com',        2),
('Evening Reporter',          'Organization', 'evening@reporter.com',   2),
('Elena Popescu',             'Person',       'elena@email.com',        2),
('Weekly Digest',             'Organization', 'weekly@digest.com',      2),
('Kofi Adu',                  'Person',       'kofi@email.com',         2),
('District Pulse',            'Organization', 'district@pulse.com',     2),
('Zara Ahmed',                'Person',       'zara@email.com',         2),
('Local Lens Media',          'Organization', 'locallens@media.com',    2),
('Ivan Petrov',               'Person',       'ivan@email.com',         2),
('Community Chronicle',       'Organization', 'community@chronicle.com',2),
('Hana Kim',                  'Person',       'hana@email.com',         2),
('Suburban Gazette',          'Organization', 'suburban@gazette.com',   2),
('Luca Romano',               'Person',       'luca@email.com',         2),
('Regional Bulletin',         'Organization', 'regional@bulletin.com',  2),
('Fatou Diallo',              'Person',       'fatou@email.com',        2),
('City Watch Media',          'Organization', 'citywatch@media.com',    2),
('Brendan Walsh',             'Person',       'brendan@email.com',      2),
('Midtown Monitor',           'Organization', 'midtown@monitor.com',    2),
('Aiko Yamamoto',             'Person',       'aiko@email.com',         2),
-- HIGH (3)
('Investigative Journal',     'Organization', 'invest@journal.com',     3),
('National News Network',     'Organization', 'nnn@news.com',           3),
('Laura Adams',               'Person',       'laura@email.com',        3),
('Global Watch Agency',       'Organization', 'global@watch.com',       3),
('International Audit Bureau','Organization', 'audit@iab.com',          3),
('Dr. Anand Mehta',           'Person',       'anand@email.com',        3),
('Reuters India',             'Organization', 'reuters@india.com',      3),
('BBC Investigations',        'Organization', 'bbc@invest.com',         3),
('Prof. Linda Chen',          'Person',       'linda@email.com',        3),
('Federal Oversight Board',   'Organization', 'fed@oversight.com',      3),
('Transparency International','Organization', 'trans@intl.com',         3),
('Dr. Samuel Osei',           'Person',       'samuel@email.com',       3),
('AP Investigations',         'Organization', 'ap@invest.com',          3),
('Justice Watch Network',     'Organization', 'justice@watch.com',      3),
('Dr. Priya Sharma',          'Person',       'priyasharm@email.com',   3),
('World Audit Agency',        'Organization', 'world@audit.com',        3),
('Prof. James Okonkwo',       'Person',       'jamesokon@email.com',    3),
('Global Integrity Watch',    'Organization', 'global@integrity.com',   3),
('Dr. Maria Santos',          'Person',       'mariasantos@email.com',  3),
('National Fraud Bureau',     'Organization', 'natfraud@bureau.com',    3),
('Prof. Ahmed Khalil',        'Person',       'ahmedkhal@email.com',    3),
('International Press Trust', 'Organization', 'intpress@trust.com',     3),
('Dr. Susan Park',            'Person',       'susanpark@email.com',    3),
('Anti Corruption Council',   'Organization', 'anticorr@council.com',   3),
('Prof. Raj Patel',           'Person',       'rajpatel@email.com',     3),
('Global Justice Monitor',    'Organization', 'global@justicemon.com',  3),
('Dr. Elena Ivanova',         'Person',       'elenaivan@email.com',    3),
('World Press Federation',    'Organization', 'world@pressfed.com',     3),
('Prof. David Mensah',        'Person',       'davidmen@email.com',     3),
('National Integrity Board',  'Organization', 'natint@board.com',       3),
('Dr. Fatima Al-Rashid',      'Person',       'fatimarash@email.com',   3),
('Global Accountability Net', 'Organization', 'global@accountnet.com',  3),
('Prof. Carlos Mendoza',      'Person',       'carlosmen@email.com',    3),
('Public Interest Watchdog',  'Organization', 'publicint@watchdog.com', 3),
('Dr. Anna Kowalski',         'Person',       'annakowal@email.com',    3),
('Truth in Reporting Agency', 'Organization', 'truth@reporting.com',    3),
('Prof. Liu Wei',             'Person',       'liuwei@email.com',       3),
('Independent Fact Bureau',   'Organization', 'indfact@bureau.com',     3),
('Dr. Kwame Asante',          'Person',       'kwameasante@email.com',  3),
('Investigative Press Guild', 'Organization', 'invpress@guild.com',     3),
('Prof. Nina Volkov',         'Person',       'ninavolk@email.com',     3),
('Global Ethics Commission',  'Organization', 'global@ethics.com',      3),
('Dr. Ravi Krishnan',         'Person',       'ravikrishn@email.com',   3),
('International Truth Watch', 'Organization', 'inttruth@watch.com',     3),
('Prof. Sara Obi',            'Person',       'saraobi@email.com',      3),
('National Audit Council',    'Organization', 'nataudit@council.com',   3),
('Dr. Hiro Tanaka',           'Person',       'hirotanaka@email.com',   3),
('Press Freedom Network',     'Organization', 'pressfree@network.com',  3),
('Prof. Amara Diallo',        'Person',       'amaradiallo@email.com',  3),
('Global Corruption Monitor', 'Organization', 'global@corrmon.com',     3),
('Dr. Lena Weber',            'Person',       'lenaweber@email.com',    3),
('Truth Accountability Board','Organization', 'truthacc@board.com',     3),
('Prof. Omar Hassan',         'Person',       'omarhassan@email.com',   3),
('Investigative Standards Net','Organization','invstand@net.com',       3),
('Dr. Sofia Petrov',          'Person',       'sofiapetrov@email.com',  3),
('Global News Standards Org', 'Organization', 'global@newsstand.com',   3),
('Prof. Kofi Boateng',        'Person',       'kofiboat@email.com',     3),
('Independent Ethics Watch',  'Organization', 'indethics@watch.com',    3),
('Dr. Mei Zhang',             'Person',       'meizhang@email.com',     3),
('World Integrity Network',   'Organization', 'world@integritynet.com', 3),
('Prof. Isabel Ferreira',     'Person',       'isabelferr@email.com',   3),
('Accountability Press',      'Organization', 'account@press.com',      3),
('Dr. Yusuf Ibrahim',         'Person',       'yusufibr@email.com',     3),
('Global Fact Check Bureau',  'Organization', 'globalfact@bureau.com',  3),
('Prof. Ana Lima',            'Person',       'analima@email.com',      3),
('Ethics in Journalism Org',  'Organization', 'ethicsjour@org.com',     3),
('Dr. Patrick Eze',           'Person',       'patrickeze@email.com',   3);

-- Interviews: LOW sources (1 each, Online)
INSERT INTO Interview (Interview_Date, Mode, Transcript, Story_ID, Source_ID) VALUES
('2025-01-10','Online','General opinion only.',1,1),
('2025-01-11','Online','Unverified claim shared.',2,2),
('2025-01-12','Online','Anonymous short tip.',3,3),
('2025-01-13','Online','Heard it from someone.',4,4),
('2025-01-14','Online','Rumor from social media.',5,5),
('2025-01-15','Online','No proof provided.',6,6),
('2025-01-16','Online','Vague statement given.',7,7),
('2025-01-17','Online','Could not verify details.',8,8),
('2025-01-18','Online','Second hand information.',9,9),
('2025-01-19','Online','Refused to provide documents.',10,10),
('2025-01-20','Online','Unsubstantiated allegations.',11,11),
('2025-01-21','Online','Clickbait story pitch.',12,12),
('2025-01-22','Online','Anonymous with no follow up.',13,13),
('2025-01-23','Online','Could not confirm source.',14,14),
('2025-01-24','Online','No evidence attached.',15,15),
('2025-01-25','Online','Vague and unverifiable.',16,16),
('2025-01-26','Online','Social media screenshot only.',17,17),
('2025-01-27','Online','Forwarded message content.',18,18),
('2025-01-28','Online','Anonymous tip no details.',19,19),
('2025-01-29','Online','Hearsay information.',20,20),
('2025-01-30','Online','Unverified social post.',21,21),
('2025-01-31','Online','No documentation provided.',22,22),
('2025-02-01','Online','Anonymous caller tip.',23,23),
('2025-02-02','Online','Could not trace source.',24,24),
('2025-02-03','Online','Rumor circulating online.',25,25),
('2025-02-04','Online','No supporting evidence.',26,26),
('2025-02-05','Online','Vague claim only.',27,27),
('2025-02-06','Online','Second hand rumor.',28,28),
('2025-02-07','Online','Unverified blog post.',29,29),
('2025-02-08','Online','Social media rumor.',30,30),
('2025-02-09','Online','Anonymous tip received.',31,31),
('2025-02-10','Online','No evidence provided.',32,32),
('2025-02-11','Online','Unverified claim made.',33,33),
('2025-02-12','Online','Could not verify.',34,34),
('2025-02-13','Online','Vague anonymous tip.',35,35),
('2025-02-14','Online','No documentation.',36,36),
('2025-02-15','Online','Unverified source.',37,37),
('2025-02-16','Online','Anonymous message.',38,38),
('2025-02-17','Online','Unsubstantiated claim.',39,39),
('2025-02-18','Online','No proof attached.',40,40),
('2025-02-19','Online','Hearsay only.',1,41),
('2025-02-20','Online','Social media claim.',2,42),
('2025-02-21','Online','Could not confirm.',3,43),
('2025-02-22','Online','Rumor shared.',4,44),
('2025-02-23','Online','Anonymous tip.',5,45),
('2025-02-24','Online','No evidence.',6,46),
('2025-02-25','Online','Vague claim.',7,47),
('2025-02-26','Online','Unverified.',8,48),
('2025-02-27','Online','Anonymous message.',9,49),
('2025-02-28','Online','No documentation.',10,50),
('2025-03-01','Online','Rumor only.',11,51),
('2025-03-02','Online','Could not verify.',12,52),
('2025-03-03','Online','Unconfirmed tip.',13,53),
('2025-03-04','Online','No proof.',14,54),
('2025-03-05','Online','Vague claim.',15,55),
('2025-03-06','Online','Anonymous source.',16,56),
('2025-03-07','Online','Unverified post.',17,57),
('2025-03-08','Online','Social media only.',18,58),
('2025-03-09','Online','No evidence.',19,59),
('2025-03-10','Online','Anonymous tip.',20,60),
('2025-03-11','Online','Unverified claim.',21,61),
('2025-03-12','Online','No documentation.',22,62),
('2025-03-13','Online','Could not confirm.',23,63),
('2025-03-14','Online','Vague rumor.',24,64),
('2025-03-15','Online','No proof provided.',25,65),
('2025-03-16','Online','Unsubstantiated.',26,66),
('2025-03-17','Online','Anonymous only.',27,67),
-- Interviews: MEDIUM sources (3 each, mixed modes)
('2025-01-15','In-person','Shared partial documents.',1,68),
('2025-01-20','Online','Explained transaction flow.',2,68),
('2025-01-25','In-person','Confirmed some details.',3,68),
('2025-01-16','Online','Fraud structure details.',4,69),
('2025-01-21','In-person','Partial evidence given.',5,69),
('2025-01-26','Online','Some records shown.',6,69),
('2025-01-17','In-person','Healthcare records partial.',7,70),
('2025-01-22','Online','Insurance docs shared.',8,70),
('2025-01-27','In-person','Partial claim confirmed.',9,70),
('2025-01-18','Online','Real estate link noted.',10,71),
('2025-01-23','In-person','Partial proof given.',11,71),
('2025-01-28','Online','Some evidence shared.',12,71),
('2025-01-19','In-person','Grant records partial.',13,72),
('2025-01-24','Online','Some details confirmed.',14,72),
('2025-01-29','In-person','Partial audit shared.',15,72),
('2025-02-01','Online','Bribery partial evidence.',16,73),
('2025-02-06','In-person','Some officer records.',17,73),
('2025-02-11','Online','Partial testimony.',18,73),
('2025-02-02','In-person','Hospital partial docs.',19,74),
('2025-02-07','Online','Drug records shared.',20,74),
('2025-02-12','In-person','Some evidence given.',21,74),
('2025-02-03','Online','Mining partial proof.',22,75),
('2025-02-08','In-person','Permit irregularities.',23,75),
('2025-02-13','Online','Some docs shared.',24,75),
('2025-02-04','In-person','School fund partial.',25,76),
('2025-02-09','Online','Diversion partial proof.',26,76),
('2025-02-14','In-person','Some records shown.',27,76),
('2025-02-05','Online','Water test partial.',28,77),
('2025-02-10','In-person','Contamination noted.',29,77),
('2025-02-15','Online','Some results shared.',30,77),
('2025-02-16','In-person','Loan irregularities.',31,78),
('2025-02-21','Online','Partial application docs.',32,78),
('2025-02-26','In-person','Some evidence shared.',33,78),
('2025-02-17','Online','Voting partial evidence.',34,79),
('2025-02-22','In-person','Machine irregularity.',35,79),
('2025-02-27','Online','Some records shown.',36,79),
('2025-02-18','In-person','Food partial evidence.',37,80),
('2025-02-23','Online','Supply chain partial.',38,80),
('2025-02-28','In-person','Some docs confirmed.',39,80),
('2025-02-19','Online','Land partial evidence.',40,81),
('2025-02-24','In-person','Acquisition partial.',1,81),
('2025-03-01','Online','Some records shared.',2,81),
('2025-02-20','In-person','Tax partial evidence.',3,82),
('2025-02-25','Online','Filing irregularities.',4,82),
('2025-03-02','In-person','Some docs shared.',5,82),
('2025-03-03','Online','Child labor partial.',6,83),
('2025-03-08','In-person','Factory records partial.',7,83),
('2025-03-13','Online','Some evidence given.',8,83),
('2025-03-04','In-person','Pharma partial docs.',9,84),
('2025-03-09','Online','Prescription partial.',10,84),
('2025-03-14','In-person','Some records shown.',11,84),
('2025-03-05','Online','Bridge partial evidence.',12,85),
('2025-03-10','In-person','Contract irregularities.',13,85),
('2025-03-15','Online','Some docs shared.',14,85),
('2025-03-06','In-person','Cyber partial evidence.',15,86),
('2025-03-11','Online','Transaction partial.',16,86),
('2025-03-16','In-person','Some records confirmed.',17,86),
('2025-03-07','Online','Arms partial evidence.',18,87),
('2025-03-12','In-person','Smuggling partial.',19,87),
('2025-03-17','Online','Some docs noted.',20,87),
('2025-03-08','In-person','Pension partial evidence.',21,88),
('2025-03-13','Online','Fund diversion partial.',22,88),
('2025-03-18','In-person','Some records shared.',23,88),
('2025-03-09','Online','Admission partial evidence.',24,89),
('2025-03-14','In-person','Scam partial docs.',25,89),
('2025-03-19','Online','Some evidence shown.',26,89),
('2025-03-10','In-person','Forest partial evidence.',27,90),
('2025-03-15','Online','Encroachment partial.',28,90),
('2025-03-20','In-person','Some records given.',29,90),
('2025-03-11','Online','Fuel partial evidence.',30,91),
('2025-03-16','In-person','Subsidy partial docs.',31,91),
('2025-03-21','Online','Some evidence shared.',32,91),
('2025-03-12','In-person','Refugee partial evidence.',33,92),
('2025-03-17','Online','Aid diversion partial.',34,92),
('2025-03-22','In-person','Some docs confirmed.',35,92),
('2025-03-13','Online','Traffic partial evidence.',36,93),
('2025-03-18','In-person','Bribery partial docs.',37,93),
('2025-03-23','Online','Some records shared.',38,93),
('2025-03-14','In-person','Medical device partial.',39,94),
('2025-03-19','Online','Device fraud partial.',40,94),
('2025-03-24','In-person','Some evidence given.',1,94),
('2025-03-15','Online','Coal partial evidence.',2,95),
('2025-03-20','In-person','Mining partial docs.',3,95),
('2025-03-25','Online','Some records noted.',4,95),
('2025-03-16','In-person','Sports partial evidence.',5,96),
('2025-03-21','Online','Betting partial docs.',6,96),
('2025-03-26','In-person','Some evidence shared.',7,96),
('2025-03-17','Online','NGO partial evidence.',8,97),
('2025-03-22','In-person','Fund misuse partial.',9,97),
('2025-03-27','Online','Some docs confirmed.',10,97),
('2025-03-18','In-person','Food import partial.',11,98),
('2025-03-23','Online','Import scandal partial.',12,98),
('2025-03-28','In-person','Some records shared.',13,98),
('2025-03-19','Online','Border partial evidence.',14,99),
('2025-03-24','In-person','Customs partial docs.',15,99),
('2025-03-29','Online','Some evidence given.',16,99),
('2025-03-20','In-person','Telecom partial evidence.',17,100),
('2025-03-25','Online','License partial docs.',18,100),
('2025-03-30','In-person','Some records shown.',19,100),
('2025-03-21','Online','Urban partial evidence.',20,101),
('2025-03-26','In-person','Planning partial docs.',21,101),
('2025-03-31','Online','Some evidence noted.',22,101),
('2025-03-22','In-person','Welfare partial evidence.',23,102),
('2025-03-27','Online','Benefits partial docs.',24,102),
('2025-04-01','In-person','Some records confirmed.',25,102),
('2025-03-23','Online','Airport partial evidence.',26,103),
('2025-03-28','In-person','Contract partial docs.',27,103),
('2025-04-02','Online','Some evidence shared.',28,103),
('2025-03-24','In-person','Pesticide partial evidence.',29,104),
('2025-03-29','Online','Crop partial docs.',30,104),
('2025-04-03','In-person','Some records given.',31,104),
('2025-03-25','Online','Prison partial evidence.',32,105),
('2025-03-30','In-person','Corruption partial docs.',33,105),
('2025-04-04','Online','Some evidence shown.',34,105),
('2025-03-26','In-person','Defense partial evidence.',35,106),
('2025-03-31','Online','Procurement partial.',36,106),
('2025-04-05','In-person','Some records shared.',37,106),
('2025-03-27','Online','City partial evidence.',38,107),
('2025-04-01','In-person','Corruption partial docs.',39,107),
('2025-04-06','Online','Some evidence noted.',40,107),
('2025-03-28','In-person','Tech partial evidence.',1,108),
('2025-04-02','Online','Fraud partial docs.',2,108),
('2025-04-07','In-person','Some records confirmed.',3,108),
('2025-03-29','Online','Env partial evidence.',4,109),
('2025-04-03','In-person','Violation partial docs.',5,109),
('2025-04-08','Online','Some evidence shared.',6,109),
('2025-03-30','In-person','Health partial evidence.',7,110),
('2025-04-04','Online','Scam partial docs.',8,110),
('2025-04-09','In-person','Some records noted.',9,110),
('2025-03-31','Online','Real estate partial.',10,111),
('2025-04-05','In-person','Laundering partial.',11,111),
('2025-04-10','Online','Some evidence given.',12,111),
('2025-04-01','In-person','Education partial.',13,112),
('2025-04-06','Online','Grant partial docs.',14,112),
('2025-04-11','In-person','Some records shared.',15,112),
('2025-04-02','Online','Police partial evidence.',16,113),
('2025-04-07','In-person','Bribery partial docs.',17,113),
('2025-04-12','Online','Some evidence confirmed.',18,113),
('2025-04-03','In-person','Hospital partial.',19,114),
('2025-04-08','Online','Drug partial docs.',20,114),
('2025-04-13','In-person','Some records shown.',21,114),
('2025-04-04','Online','Mining partial.',22,115),
('2025-04-09','In-person','Permit partial docs.',23,115),
('2025-04-14','Online','Some evidence noted.',24,115),
('2025-04-05','In-person','School partial.',25,116),
('2025-04-10','Online','Fund partial docs.',26,116),
('2025-04-15','In-person','Some records given.',27,116),
('2025-04-06','Online','Water partial.',28,117),
('2025-04-11','In-person','Contamination partial.',29,117),
('2025-04-16','Online','Some evidence shared.',30,117),
('2025-04-07','In-person','Bank partial.',31,118),
('2025-04-12','Online','Loan partial docs.',32,118),
('2025-04-17','In-person','Some records confirmed.',33,118),
('2025-04-08','Online','Election partial.',34,119),
('2025-04-13','In-person','Rigging partial docs.',35,119),
('2025-04-18','Online','Some evidence noted.',36,119),
('2025-04-09','In-person','Food partial.',37,120),
('2025-04-14','Online','Adulteration partial.',38,120),
('2025-04-19','In-person','Some records shared.',39,120),
('2025-04-10','Online','Land partial.',40,121),
('2025-04-15','In-person','Grabbing partial docs.',1,121),
('2025-04-20','Online','Some evidence given.',2,121),
('2025-04-11','In-person','Tax partial.',3,122),
('2025-04-16','Online','Evasion partial docs.',4,122),
('2025-04-21','In-person','Some records noted.',5,122),
('2025-04-12','Online','Child labor partial.',6,123),
('2025-04-17','In-person','Factory partial docs.',7,123),
('2025-04-22','Online','Some evidence confirmed.',8,123),
('2025-04-13','In-person','Pharma partial.',9,124),
('2025-04-18','Online','Kickback partial docs.',10,124),
('2025-04-23','In-person','Some records shared.',11,124),
('2025-04-14','Online','Infra partial.',12,125),
('2025-04-19','In-person','Scam partial docs.',13,125),
('2025-04-24','Online','Some evidence shown.',14,125),
('2025-04-15','In-person','Cyber partial.',15,126),
('2025-04-20','Online','Fraud partial docs.',16,126),
('2025-04-25','In-person','Some records given.',17,126),
('2025-04-16','Online','Arms partial.',18,127),
('2025-04-21','In-person','Smuggling partial docs.',19,127),
('2025-04-26','Online','Some evidence noted.',20,127),
('2025-04-17','In-person','Pension partial.',21,128),
('2025-04-22','Online','Fund partial docs.',22,128),
('2025-04-27','In-person','Some records confirmed.',23,128),
('2025-04-18','Online','Admission partial.',24,129),
('2025-04-23','In-person','Scam partial docs.',25,129),
('2025-04-28','Online','Some evidence shared.',26,129),
('2025-04-19','In-person','Forest partial.',27,130),
('2025-04-24','Online','Encroachment partial.',28,130),
('2025-04-29','In-person','Some records noted.',29,130),
('2025-04-20','Online','Fuel partial.',30,131),
('2025-04-25','In-person','Subsidy partial docs.',31,131),
('2025-04-30','Online','Some evidence given.',32,131),
('2025-04-21','In-person','Refugee partial.',33,132),
('2025-04-26','Online','Aid partial docs.',34,132),
('2025-05-01','In-person','Some records shown.',35,132),
('2025-04-22','Online','Traffic partial.',36,133),
('2025-04-27','In-person','Bribery partial docs.',37,133),
('2025-05-02','Online','Some evidence confirmed.',38,133),
('2025-04-23','In-person','Medical partial.',39,134),
('2025-04-28','Online','Device partial docs.',40,134),
('2025-05-03','In-person','Some records shared.',1,134),
-- Interviews: HIGH sources (7 each, mostly In-person)
('2025-01-18','In-person','Detailed corruption evidence with documents.',1,135),
('2025-01-20','In-person','Multiple supporting docs verified.',1,135),
('2025-01-22','Online','Cross referenced bank records.',2,135),
('2025-01-24','In-person','Official statement confirmed.',3,135),
('2025-01-26','Online','Lab results verified.',4,135),
('2025-01-28','In-person','Full audit trail documented.',5,135),
('2025-01-30','Online','Final evidence compiled.',6,135),
('2025-02-01','In-person','CEO fraud admission on record.',7,136),
('2025-02-03','In-person','Bank verification proof submitted.',8,136),
('2025-02-05','Online','Financial records cross checked.',9,136),
('2025-02-07','In-person','Witness testimony verified.',10,136),
('2025-02-09','Online','Document authentication done.',11,136),
('2025-02-11','In-person','Complete evidence chain done.',12,136),
('2025-02-13','Online','All records confirmed.',13,136),
('2025-02-15','In-person','Environmental lab confirmed.',14,137),
('2025-02-17','Online','Satellite images analyzed.',15,137),
('2025-02-19','In-person','Expert testimony recorded.',16,137),
('2025-02-21','Online','All docs verified.',17,137),
('2025-02-23','In-person','Full evidence documented.',18,137),
('2025-02-25','Online','Records authenticated.',19,137),
('2025-02-27','In-person','Final report confirmed.',20,137),
('2025-03-01','In-person','Property chain documented.',21,138),
('2025-03-03','Online','Money trail confirmed.',22,138),
('2025-03-05','In-person','Financial records verified.',23,138),
('2025-03-07','Online','Witness accounts confirmed.',24,138),
('2025-03-09','In-person','All evidence compiled.',25,138),
('2025-03-11','Online','Documents authenticated.',26,138),
('2025-03-13','In-person','Full audit completed.',27,138),
('2025-03-15','In-person','Grant misuse documented.',28,139),
('2025-03-17','Online','All records verified.',29,139),
('2025-03-19','In-person','Expert testimony done.',30,139),
('2025-03-21','Online','Evidence chain complete.',31,139),
('2025-03-23','In-person','Documents confirmed.',32,139),
('2025-03-25','Online','Full proof compiled.',33,139),
('2025-03-27','In-person','Final evidence noted.',34,139),
('2025-03-29','In-person','Bribery records confirmed.',35,140),
('2025-03-31','Online','Officer testimony verified.',36,140),
('2025-04-02','In-person','All records documented.',37,140),
('2025-04-04','Online','Evidence authenticated.',38,140),
('2025-04-06','In-person','Witness confirmed.',39,140),
('2025-04-08','Online','Full report done.',40,140),
('2025-04-10','In-person','Final audit complete.',1,140),
('2025-01-19','In-person','Drug batch tested confirmed.',2,141),
('2025-01-21','Online','Hospital procurement verified.',3,141),
('2025-01-23','In-person','All records documented.',4,141),
('2025-01-25','Online','Evidence chain complete.',5,141),
('2025-01-27','In-person','Expert testimony done.',6,141),
('2025-01-29','Online','Documents authenticated.',7,141),
('2025-01-31','In-person','Final report confirmed.',8,141),
('2025-02-02','In-person','Mining permit confirmed.',9,142),
('2025-02-04','Online','Official signatures verified.',10,142),
('2025-02-06','In-person','All docs confirmed.',11,142),
('2025-02-08','Online','Witness testimony done.',12,142),
('2025-02-10','In-person','Records authenticated.',13,142),
('2025-02-12','Online','Evidence compiled.',14,142),
('2025-02-14','In-person','Full audit complete.',15,142),
('2025-02-16','In-person','School fund diversion traced.',16,143),
('2025-02-18','Online','Bank statements cross referenced.',17,143),
('2025-02-20','In-person','All records verified.',18,143),
('2025-02-22','Online','Witness confirmed.',19,143),
('2025-02-24','In-person','Documents authenticated.',20,143),
('2025-02-26','Online','Evidence chain complete.',21,143),
('2025-02-28','In-person','Final report done.',22,143),
('2025-03-02','In-person','Water contamination confirmed.',23,144),
('2025-03-04','Online','Municipality cover-up documented.',24,144),
('2025-03-06','In-person','Lab results verified.',25,144),
('2025-03-08','Online','Expert testimony done.',26,144),
('2025-03-10','In-person','All records confirmed.',27,144),
('2025-03-12','Online','Evidence authenticated.',28,144),
('2025-03-14','In-person','Full audit complete.',29,144),
('2025-03-16','In-person','Bank loan fraud verified.',30,145),
('2025-03-18','Online','Fake applicants confirmed.',31,145),
('2025-03-20','In-person','All docs verified.',32,145),
('2025-03-22','Online','Witness testimony done.',33,145),
('2025-03-24','In-person','Records authenticated.',34,145),
('2025-03-26','Online','Evidence compiled.',35,145),
('2025-03-28','In-person','Final report confirmed.',36,145),
('2025-03-30','In-person','Voting machine expert done.',37,146),
('2025-04-01','Online','Election records reviewed.',38,146),
('2025-04-03','In-person','All evidence documented.',39,146),
('2025-04-05','Online','Witness confirmed.',40,146),
('2025-04-07','In-person','Documents verified.',1,146),
('2025-04-09','Online','Evidence chain complete.',2,146),
('2025-04-11','In-person','Final audit done.',3,146),
('2025-04-13','In-person','Food lab confirmed.',4,147),
('2025-04-15','Online','Supply chain mapped.',5,147),
('2025-04-17','In-person','All records verified.',6,147),
('2025-04-19','Online','Expert testimony done.',7,147),
('2025-04-21','In-person','Documents authenticated.',8,147),
('2025-04-23','Online','Evidence compiled.',9,147),
('2025-04-25','In-person','Final report complete.',10,147),
('2025-01-20','In-person','Land fraud documented.',11,148),
('2025-01-22','Online','Farmer testimonies verified.',12,148),
('2025-01-24','In-person','All records confirmed.',13,148),
('2025-01-26','Online','Witness done.',14,148),
('2025-01-28','In-person','Documents authenticated.',15,148),
('2025-01-30','Online','Evidence chain complete.',16,148),
('2025-02-01','In-person','Final audit done.',17,148),
('2025-02-03','In-person','Tax records confirmed.',18,149),
('2025-02-05','Online','Corporate filings checked.',19,149),
('2025-02-07','In-person','All docs verified.',20,149),
('2025-02-09','Online','Witness testimony.',21,149),
('2025-02-11','In-person','Records authenticated.',22,149),
('2025-02-13','Online','Evidence compiled.',23,149),
('2025-02-15','In-person','Full report done.',24,149),
('2025-02-17','In-person','Factory inspection done.',25,150),
('2025-02-19','Online','Factory records verified.',26,150),
('2025-02-21','In-person','All evidence documented.',27,150),
('2025-02-23','Online','Witness confirmed.',28,150),
('2025-02-25','In-person','Documents authenticated.',29,150),
('2025-02-27','Online','Evidence chain complete.',30,150),
('2025-03-01','In-person','Final audit done.',31,150),
('2025-03-03','In-person','Pharma payments traced.',32,151),
('2025-03-05','Online','Prescription data verified.',33,151),
('2025-03-07','In-person','All records confirmed.',34,151),
('2025-03-09','Online','Witness testimony done.',35,151),
('2025-03-11','In-person','Documents authenticated.',36,151),
('2025-03-13','Online','Evidence compiled.',37,151),
('2025-03-15','In-person','Final report complete.',38,151),
('2025-03-17','In-person','Bridge fund confirmed.',39,152),
('2025-03-19','Online','Contractor fraud filed.',40,152),
('2025-03-21','In-person','All evidence documented.',1,152),
('2025-03-23','Online','Witness confirmed.',2,152),
('2025-03-25','In-person','Documents verified.',3,152),
('2025-03-27','Online','Evidence chain complete.',4,152),
('2025-03-29','In-person','Final audit done.',5,152),
('2025-03-31','In-person','Cyber network mapped.',6,153),
('2025-04-02','Online','Bank logs verified.',7,153),
('2025-04-04','In-person','All records confirmed.',8,153),
('2025-04-06','Online','Witness testimony.',9,153),
('2025-04-08','In-person','Documents authenticated.',10,153),
('2025-04-10','Online','Evidence compiled.',11,153),
('2025-04-12','In-person','Full report done.',12,153),
('2025-04-14','In-person','Arms evidence confirmed.',13,154),
('2025-04-16','Online','Smuggling documented.',14,154),
('2025-04-18','In-person','All records verified.',15,154),
('2025-04-20','Online','Witness done.',16,154),
('2025-04-22','In-person','Documents authenticated.',17,154),
('2025-04-24','Online','Evidence chain complete.',18,154),
('2025-04-26','In-person','Final audit done.',19,154),
('2025-04-28','In-person','Pension fraud confirmed.',20,155),
('2025-04-30','Online','Fund diversion documented.',21,155),
('2025-05-02','In-person','All records verified.',22,155),
('2025-05-04','Online','Witness confirmed.',23,155),
('2025-05-06','In-person','Documents authenticated.',24,155),
('2025-05-08','Online','Evidence compiled.',25,155),
('2025-05-10','In-person','Final report complete.',26,155),
('2025-01-21','In-person','Admission scam confirmed.',27,156),
('2025-01-23','Online','Bribe records documented.',28,156),
('2025-01-25','In-person','All evidence confirmed.',29,156),
('2025-01-27','Online','Witness done.',30,156),
('2025-01-29','In-person','Documents verified.',31,156),
('2025-01-31','Online','Evidence chain complete.',32,156),
('2025-02-02','In-person','Full audit done.',33,156),
('2025-02-04','In-person','Forest encroachment confirmed.',34,157),
('2025-02-06','Online','Protected land documented.',35,157),
('2025-02-08','In-person','All records verified.',36,157),
('2025-02-10','Online','Witness testimony.',37,157),
('2025-02-12','In-person','Documents authenticated.',38,157),
('2025-02-14','Online','Evidence compiled.',39,157),
('2025-02-16','In-person','Final report done.',40,157),
('2025-02-18','In-person','Fuel fraud confirmed.',1,158),
('2025-02-20','Online','Subsidy claims documented.',2,158),
('2025-02-22','In-person','All evidence verified.',3,158),
('2025-02-24','Online','Witness done.',4,158),
('2025-02-26','In-person','Documents authenticated.',5,158),
('2025-02-28','Online','Evidence compiled.',6,158),
('2025-03-02','In-person','Full audit complete.',7,158),
('2025-03-04','In-person','Aid diversion confirmed.',8,159),
('2025-03-06','Online','Refugee funds documented.',9,159),
('2025-03-08','In-person','All records verified.',10,159),
('2025-03-10','Online','Witness testimony done.',11,159),
('2025-03-12','In-person','Documents authenticated.',12,159),
('2025-03-14','Online','Evidence chain complete.',13,159),
('2025-03-16','In-person','Final report done.',14,159),
('2025-03-18','In-person','Traffic bribery confirmed.',15,160),
('2025-03-20','Online','Officer extortion documented.',16,160),
('2025-03-22','In-person','All evidence verified.',17,160),
('2025-03-24','Online','Witness confirmed.',18,160),
('2025-03-26','In-person','Documents authenticated.',19,160),
('2025-03-28','Online','Evidence compiled.',20,160),
('2025-03-30','In-person','Full audit done.',21,160),
('2025-04-01','In-person','Medical device fraud confirmed.',22,161),
('2025-04-03','Online','Substandard docs documented.',23,161),
('2025-04-05','In-person','All records verified.',24,161),
('2025-04-07','Online','Witness done.',25,161),
('2025-04-09','In-person','Documents authenticated.',26,161),
('2025-04-11','Online','Evidence compiled.',27,161),
('2025-04-13','In-person','Full report complete.',28,161),
('2025-04-15','In-person','Coal mining confirmed.',29,162),
('2025-04-17','Online','Illegal extraction documented.',30,162),
('2025-04-19','In-person','All evidence verified.',31,162),
('2025-04-21','Online','Witness testimony.',32,162),
('2025-04-23','In-person','Documents authenticated.',33,162),
('2025-04-25','Online','Evidence chain complete.',34,162),
('2025-04-27','In-person','Final audit done.',35,162),
('2025-04-29','In-person','Match fixing confirmed.',36,163),
('2025-05-01','Online','Organized crime documented.',37,163),
('2025-05-03','In-person','All records verified.',38,163),
('2025-05-05','Online','Witness done.',39,163),
('2025-05-07','In-person','Documents authenticated.',40,163),
('2025-05-09','Online','Evidence compiled.',1,163),
('2025-05-11','In-person','Full report done.',2,163),
('2025-01-22','In-person','NGO fraud confirmed.',3,164),
('2025-01-24','Online','Charity funds documented.',4,164),
('2025-01-26','In-person','All evidence verified.',5,164),
('2025-01-28','Online','Witness done.',6,164),
('2025-01-30','In-person','Documents authenticated.',7,164),
('2025-02-01','Online','Evidence compiled.',8,164),
('2025-02-03','In-person','Full audit complete.',9,164),
('2025-02-05','In-person','Food import confirmed.',10,165),
('2025-02-07','Online','Contamination documented.',11,165),
('2025-02-09','In-person','All records verified.',12,165),
('2025-02-11','Online','Witness testimony done.',13,165),
('2025-02-13','In-person','Documents authenticated.',14,165),
('2025-02-15','Online','Evidence chain complete.',15,165),
('2025-02-17','In-person','Final report done.',16,165),
('2025-02-19','In-person','Border fraud confirmed.',17,166),
('2025-02-21','Online','Smuggling documented.',18,166),
('2025-02-23','In-person','All evidence verified.',19,166),
('2025-02-25','Online','Witness confirmed.',20,166),
('2025-02-27','In-person','Documents authenticated.',21,166),
('2025-03-01','Online','Evidence compiled.',22,166),
('2025-03-03','In-person','Full audit done.',23,166),
('2025-03-05','In-person','Telecom fraud confirmed.',24,167),
('2025-03-07','Online','License scam documented.',25,167),
('2025-03-09','In-person','All records verified.',26,167),
('2025-03-11','Online','Witness done.',27,167),
('2025-03-13','In-person','Documents authenticated.',28,167),
('2025-03-15','Online','Evidence compiled.',29,167),
('2025-03-17','In-person','Full report complete.',30,167),
('2025-03-19','In-person','Urban corruption confirmed.',31,168),
('2025-03-21','Online','Zoning fraud documented.',32,168),
('2025-03-23','In-person','All evidence verified.',33,168),
('2025-03-25','Online','Witness testimony.',34,168),
('2025-03-27','In-person','Documents authenticated.',35,168),
('2025-03-29','Online','Evidence chain complete.',36,168),
('2025-03-31','In-person','Final audit done.',37,168),
('2025-04-02','In-person','Welfare fraud confirmed.',38,169),
('2025-04-04','Online','Benefits fraud documented.',39,169),
('2025-04-06','In-person','All records verified.',40,169),
('2025-04-08','Online','Witness done.',1,169),
('2025-04-10','In-person','Documents authenticated.',2,169),
('2025-04-12','Online','Evidence compiled.',3,169),
('2025-04-14','In-person','Full report done.',4,169),
('2025-04-16','In-person','Airport fraud confirmed.',5,170),
('2025-04-18','Online','Contract scam documented.',6,170),
('2025-04-20','In-person','All evidence verified.',7,170),
('2025-04-22','Online','Witness confirmed.',8,170),
('2025-04-24','In-person','Documents authenticated.',9,170),
('2025-04-26','Online','Evidence compiled.',10,170),
('2025-04-28','In-person','Full audit complete.',11,170),
('2025-04-30','In-person','Pesticide fraud confirmed.',12,171),
('2025-05-02','Online','Crop contamination documented.',13,171),
('2025-05-04','In-person','All records verified.',14,171),
('2025-05-06','Online','Witness testimony done.',15,171),
('2025-05-08','In-person','Documents authenticated.',16,171),
('2025-05-10','Online','Evidence chain complete.',17,171),
('2025-05-12','In-person','Final report done.',18,171),
('2025-01-23','In-person','Prison corruption confirmed.',19,172),
('2025-01-25','Online','Guard activity documented.',20,172),
('2025-01-27','In-person','All evidence verified.',21,172),
('2025-01-29','Online','Witness done.',22,172),
('2025-01-31','In-person','Documents authenticated.',23,172),
('2025-02-02','Online','Evidence compiled.',24,172),
('2025-02-04','In-person','Full audit done.',25,172),
('2025-02-06','In-person','Defense fraud confirmed.',26,173),
('2025-02-08','Online','Overbilling documented.',27,173),
('2025-02-10','In-person','All records verified.',28,173),
('2025-02-12','Online','Witness testimony.',29,173),
('2025-02-14','In-person','Documents authenticated.',30,173),
('2025-02-16','Online','Evidence compiled.',31,173),
('2025-02-18','In-person','Full report complete.',32,173),
('2025-02-20','In-person','City corruption confirmed.',33,174),
('2025-02-22','Online','Fund misuse documented.',34,174),
('2025-02-24','In-person','All evidence verified.',35,174),
('2025-02-26','Online','Witness done.',36,174),
('2025-02-28','In-person','Documents authenticated.',37,174),
('2025-03-02','Online','Evidence chain complete.',38,174),
('2025-03-04','In-person','Final audit done.',39,174),
('2025-03-06','In-person','Tech fraud confirmed.',40,175),
('2025-03-08','Online','Startup fraud documented.',1,175),
('2025-03-10','In-person','All records verified.',2,175),
('2025-03-12','Online','Witness done.',3,175),
('2025-03-14','In-person','Documents authenticated.',4,175),
('2025-03-16','Online','Evidence compiled.',5,175),
('2025-03-18','In-person','Full report done.',6,175),
('2025-03-20','In-person','Env violation confirmed.',7,176),
('2025-03-22','Online','Dumping documented.',8,176),
('2025-03-24','In-person','All evidence verified.',9,176),
('2025-03-26','Online','Witness testimony.',10,176),
('2025-03-28','In-person','Documents authenticated.',11,176),
('2025-03-30','Online','Evidence compiled.',12,176),
('2025-04-01','In-person','Full audit complete.',13,176),
('2025-04-03','In-person','Health scam confirmed.',14,177),
('2025-04-05','Online','Insurance fraud documented.',15,177),
('2025-04-07','In-person','All records verified.',16,177),
('2025-04-09','Online','Witness done.',17,177),
('2025-04-11','In-person','Documents authenticated.',18,177),
('2025-04-13','Online','Evidence chain complete.',19,177),
('2025-04-15','In-person','Final report done.',20,177),
('2025-04-17','In-person','Real estate confirmed.',21,178),
('2025-04-19','Online','Laundering documented.',22,178),
('2025-04-21','In-person','All evidence verified.',23,178),
('2025-04-23','Online','Witness confirmed.',24,178),
('2025-04-25','In-person','Documents authenticated.',25,178),
('2025-04-27','Online','Evidence compiled.',26,178),
('2025-04-29','In-person','Full audit done.',27,178),
('2025-05-01','In-person','Grant fraud confirmed.',28,179),
('2025-05-03','Online','Education funds documented.',29,179),
('2025-05-05','In-person','All records verified.',30,179),
('2025-05-07','Online','Witness done.',31,179),
('2025-05-09','In-person','Documents authenticated.',32,179),
('2025-05-11','Online','Evidence compiled.',33,179),
('2025-05-13','In-person','Full report complete.',34,179),
('2025-01-24','In-person','Police bribery confirmed.',35,180),
('2025-01-26','Online','Officer bribes documented.',36,180),
('2025-01-28','In-person','All evidence verified.',37,180),
('2025-01-30','Online','Witness done.',38,180),
('2025-02-01','In-person','Documents authenticated.',39,180),
('2025-02-03','Online','Evidence chain complete.',40,180),
('2025-02-05','In-person','Final audit done.',1,180),
('2025-02-07','In-person','Drug scam confirmed.',2,181),
('2025-02-09','Online','Medicines documented.',3,181),
('2025-02-11','In-person','All records verified.',4,181),
('2025-02-13','Online','Witness testimony.',5,181),
('2025-02-15','In-person','Documents authenticated.',6,181),
('2025-02-17','Online','Evidence compiled.',7,181),
('2025-02-19','In-person','Full report done.',8,181),
('2025-02-21','In-person','Mining fraud confirmed.',9,182),
('2025-02-23','Online','Permit fraud documented.',10,182),
('2025-02-25','In-person','All evidence verified.',11,182),
('2025-02-27','Online','Witness done.',12,182),
('2025-03-01','In-person','Documents authenticated.',13,182),
('2025-03-03','Online','Evidence compiled.',14,182),
('2025-03-05','In-person','Full audit complete.',15,182),
('2025-03-07','In-person','School fraud confirmed.',16,183),
('2025-03-09','Online','Fund diversion documented.',17,183),
('2025-03-11','In-person','All records verified.',18,183),
('2025-03-13','Online','Witness testimony.',19,183),
('2025-03-15','In-person','Documents authenticated.',20,183),
('2025-03-17','Online','Evidence chain complete.',21,183),
('2025-03-19','In-person','Final report done.',22,183),
('2025-03-21','In-person','Water scam confirmed.',23,184),
('2025-03-23','Online','Contamination documented.',24,184),
('2025-03-25','In-person','All evidence verified.',25,184),
('2025-03-27','Online','Witness done.',26,184),
('2025-03-29','In-person','Documents authenticated.',27,184),
('2025-03-31','Online','Evidence compiled.',28,184),
('2025-04-02','In-person','Full audit done.',29,184),
('2025-04-04','In-person','Bank fraud confirmed.',30,185),
('2025-04-06','Online','Loan fraud documented.',31,185),
('2025-04-08','In-person','All records verified.',32,185),
('2025-04-10','Online','Witness done.',33,185),
('2025-04-12','In-person','Documents authenticated.',34,185),
('2025-04-14','Online','Evidence compiled.',35,185),
('2025-04-16','In-person','Full report complete.',36,185),
('2025-04-18','In-person','Election fraud confirmed.',37,186),
('2025-04-20','Online','Rigging documented.',38,186),
('2025-04-22','In-person','All evidence verified.',39,186),
('2025-04-24','Online','Witness testimony.',40,186),
('2025-04-26','In-person','Documents authenticated.',1,186),
('2025-04-28','Online','Evidence chain complete.',2,186),
('2025-04-30','In-person','Final audit done.',3,186),
('2025-05-02','In-person','Food fraud confirmed.',4,187),
('2025-05-04','Online','Adulteration documented.',5,187),
('2025-05-06','In-person','All records verified.',6,187),
('2025-05-08','Online','Witness done.',7,187),
('2025-05-10','In-person','Documents authenticated.',8,187),
('2025-05-12','Online','Evidence compiled.',9,187),
('2025-05-14','In-person','Full report done.',10,187),
('2025-01-25','In-person','Land fraud confirmed.',11,188),
('2025-01-27','Online','Grabbing documented.',12,188),
('2025-01-29','In-person','All evidence verified.',13,188),
('2025-01-31','Online','Witness done.',14,188),
('2025-02-02','In-person','Documents authenticated.',15,188),
('2025-02-04','Online','Evidence chain complete.',16,188),
('2025-02-06','In-person','Full audit done.',17,188),
('2025-02-08','In-person','Tax fraud confirmed.',18,189),
('2025-02-10','Online','Evasion documented.',19,189),
('2025-02-12','In-person','All records verified.',20,189),
('2025-02-14','Online','Witness testimony.',21,189),
('2025-02-16','In-person','Documents authenticated.',22,189),
('2025-02-18','Online','Evidence compiled.',23,189),
('2025-02-20','In-person','Full report complete.',24,189),
('2025-02-22','In-person','Child labor confirmed.',25,190),
('2025-02-24','Online','Factory fraud documented.',26,190),
('2025-02-26','In-person','All evidence verified.',27,190),
('2025-02-28','Online','Witness done.',28,190),
('2025-03-02','In-person','Documents authenticated.',29,190),
('2025-03-04','Online','Evidence compiled.',30,190),
('2025-03-06','In-person','Full audit done.',31,190),
('2025-03-08','In-person','Pharma fraud confirmed.',32,191),
('2025-03-10','Online','Kickbacks documented.',33,191),
('2025-03-12','In-person','All records verified.',34,191),
('2025-03-14','Online','Witness done.',35,191),
('2025-03-16','In-person','Documents authenticated.',36,191),
('2025-03-18','Online','Evidence chain complete.',37,191),
('2025-03-20','In-person','Final report done.',38,191),
('2025-03-22','In-person','Infra fraud confirmed.',39,192),
('2025-03-24','Online','Bridge fraud documented.',40,192),
('2025-03-26','In-person','All evidence verified.',1,192),
('2025-03-28','Online','Witness testimony.',2,192),
('2025-03-30','In-person','Documents authenticated.',3,192),
('2025-04-01','Online','Evidence compiled.',4,192),
('2025-04-03','In-person','Full audit complete.',5,192),
('2025-04-05','In-person','Cyber fraud confirmed.',6,193),
('2025-04-07','Online','Network documented.',7,193),
('2025-04-09','In-person','All records verified.',8,193),
('2025-04-11','Online','Witness done.',9,193),
('2025-04-13','In-person','Documents authenticated.',10,193),
('2025-04-15','Online','Evidence compiled.',11,193),
('2025-04-17','In-person','Full report done.',12,193),
('2025-04-19','In-person','Arms fraud confirmed.',13,194),
('2025-04-21','Online','Smuggling documented.',14,194),
('2025-04-23','In-person','All evidence verified.',15,194),
('2025-04-25','Online','Witness done.',16,194),
('2025-04-27','In-person','Documents authenticated.',17,194),
('2025-04-29','Online','Evidence chain complete.',18,194),
('2025-05-01','In-person','Final audit done.',19,194),
('2025-05-03','In-person','Pension fraud confirmed.',20,195),
('2025-05-05','Online','Fund theft documented.',21,195),
('2025-05-07','In-person','All records verified.',22,195),
('2025-05-09','Online','Witness testimony.',23,195),
('2025-05-11','In-person','Documents authenticated.',24,195),
('2025-05-13','Online','Evidence compiled.',25,195),
('2025-05-15','In-person','Full report complete.',26,195),
('2025-01-26','In-person','Admission scam confirmed.',27,196),
('2025-01-28','Online','Bribe chain documented.',28,196),
('2025-01-30','In-person','All evidence verified.',29,196),
('2025-02-01','Online','Witness done.',30,196),
('2025-02-03','In-person','Documents authenticated.',31,196),
('2025-02-05','Online','Evidence compiled.',32,196),
('2025-02-07','In-person','Full audit done.',33,196),
('2025-02-09','In-person','Forest fraud confirmed.',34,197),
('2025-02-11','Online','Encroachment documented.',35,197),
('2025-02-13','In-person','All records verified.',36,197),
('2025-02-15','Online','Witness done.',37,197),
('2025-02-17','In-person','Documents authenticated.',38,197),
('2025-02-19','Online','Evidence chain complete.',39,197),
('2025-02-21','In-person','Final report done.',40,197),
('2025-02-23','In-person','Fuel fraud confirmed.',1,198),
('2025-02-25','Online','Subsidy fraud documented.',2,198),
('2025-02-27','In-person','All evidence verified.',3,198),
('2025-03-01','Online','Witness done.',4,198),
('2025-03-03','In-person','Documents authenticated.',5,198),
('2025-03-05','Online','Evidence compiled.',6,198),
('2025-03-07','In-person','Full audit complete.',7,198),
('2025-03-09','In-person','Refugee fraud confirmed.',8,199),
('2025-03-11','Online','Aid diversion documented.',9,199),
('2025-03-13','In-person','All records verified.',10,199),
('2025-03-15','Online','Witness testimony.',11,199),
('2025-03-17','In-person','Documents authenticated.',12,199),
('2025-03-19','Online','Evidence compiled.',13,199),
('2025-03-21','In-person','Full report done.',14,199),
('2025-03-23','In-person','Traffic fraud confirmed.',15,200),
('2025-03-25','Online','Bribery documented.',16,200),
('2025-03-27','In-person','All evidence verified.',17,200),
('2025-03-29','Online','Witness done.',18,200),
('2025-03-31','In-person','Documents authenticated.',19,200),
('2025-04-02','Online','Evidence chain complete.',20,200),
('2025-04-04','In-person','Final audit done.',21,200);

-- Documents (one per story)
INSERT INTO Document (Title, Type, Upload_Date, Story_ID) VALUES
('City Budget Report',              'PDF',   '2025-01-05', 1),
('Startup Bank Records',            'Excel', '2025-02-18', 2),
('Environmental Inspection Report', 'PDF',   '2025-03-03', 3),
('Insurance Claim Files',           'PDF',   '2025-03-20', 4),
('Property Ownership Docs',         'PDF',   '2025-04-02', 5),
('Education Grant Audit',           'PDF',   '2025-04-12', 6),
('Police Internal Report',          'PDF',   '2025-01-20', 7),
('Hospital Drug Procurement',       'Excel', '2025-02-05', 8),
('Mining Permit Applications',      'PDF',   '2025-02-22', 9),
('School Financial Records',        'Excel', '2025-03-08', 10),
('Water Quality Test Results',      'PDF',   '2025-03-22', 11),
('Loan Application Records',        'Excel', '2025-04-07', 12),
('Election Commission Records',     'PDF',   '2025-01-12', 13),
('Food Lab Test Reports',           'PDF',   '2025-02-17', 14),
('Land Acquisition Documents',      'PDF',   '2025-03-12', 15),
('Corporate Tax Filings',           'Excel', '2025-04-03', 16),
('Factory Inspection Reports',      'PDF',   '2025-01-27', 17),
('Pharma Prescription Data',        'Excel', '2025-03-01', 18),
('Bridge Construction Contracts',   'PDF',   '2025-03-27', 19),
('Cyber Fraud Transaction Logs',    'Excel', '2025-04-17', 20),
('Arms Seizure Report',             'PDF',   '2025-01-08', 21),
('Pension Fund Statements',         'Excel', '2025-02-10', 22),
('University Admission Records',    'PDF',   '2025-03-14', 23),
('Forest Survey Report',            'PDF',   '2025-04-10', 24),
('Fuel Subsidy Claims',             'Excel', '2025-01-20', 25),
('Refugee Aid Distribution',        'PDF',   '2025-02-27', 26),
('Traffic Fine Records',            'Excel', '2025-03-20', 27),
('Medical Device Approval Docs',    'PDF',   '2025-04-14', 28),
('Coal Mining License Docs',        'PDF',   '2025-01-24', 29),
('Sports Betting Records',          'Excel', '2025-02-20', 30),
('NGO Financial Statements',        'PDF',   '2025-03-24', 31),
('Food Import Clearance Docs',      'PDF',   '2025-04-20', 32),
('Customs Clearance Records',       'Excel', '2025-01-30', 33),
('Telecom License Applications',    'PDF',   '2025-02-24', 34),
('Urban Planning Permits',          'PDF',   '2025-03-30', 35),
('Social Welfare Claim Records',    'Excel', '2025-04-24', 36),
('Airport Contract Documents',      'PDF',   '2025-02-01', 37),
('Pesticide Usage Reports',         'PDF',   '2025-02-28', 38),
('Prison Activity Logs',            'Excel', '2025-04-01', 39),
('Defense Procurement Files',       'PDF',   '2025-04-27', 40);

-- Locations
INSERT INTO Location (Place_Name, City, State, Country, Story_ID) VALUES
('City Hall',             'New York',      'NY', 'USA', 1),
('Startup HQ',            'San Francisco', 'CA', 'USA', 2),
('River Delta',           'Houston',       'TX', 'USA', 3),
('Insurance Office',      'Chicago',       'IL', 'USA', 4),
('Real Estate Office',    'Miami',         'FL', 'USA', 5),
('Education Board',       'Boston',        'MA', 'USA', 6),
('Police Station',        'Dallas',        'TX', 'USA', 7),
('City Hospital',         'Seattle',       'WA', 'USA', 8),
('Mining Site',           'Denver',        'CO', 'USA', 9),
('School District HQ',    'Phoenix',       'AZ', 'USA', 10),
('Water Treatment Plant', 'Portland',      'OR', 'USA', 11),
('Regional Bank',         'Atlanta',       'GA', 'USA', 12),
('Election Commission',   'Washington',    'DC', 'USA', 13),
('Food Processing Plant', 'Minneapolis',   'MN', 'USA', 14),
('Agriculture Office',    'Kansas City',   'MO', 'USA', 15),
('Tax Office',            'Detroit',       'MI', 'USA', 16),
('Factory Zone',          'Cleveland',     'OH', 'USA', 17),
('Pharmacy Chain HQ',     'Nashville',     'TN', 'USA', 18),
('Construction Site',     'Charlotte',     'NC', 'USA', 19),
('Cyber Crime Division',  'San Jose',      'CA', 'USA', 20),
('Border Checkpoint',     'El Paso',       'TX', 'USA', 21),
('Pension Office',        'Philadelphia',  'PA', 'USA', 22),
('University Campus',     'Austin',        'TX', 'USA', 23),
('National Forest',       'Sacramento',    'CA', 'USA', 24),
('Fuel Depot',            'Houston',       'TX', 'USA', 25),
('Refugee Camp',          'San Diego',     'CA', 'USA', 26),
('Traffic Division',      'Las Vegas',     'NV', 'USA', 27),
('Medical Board Office',  'Baltimore',     'MD', 'USA', 28),
('Coal Mine Site',        'Pittsburgh',    'PA', 'USA', 29),
('Sports Arena',          'Indianapolis',  'IN', 'USA', 30),
('NGO Office',            'Columbus',      'OH', 'USA', 31),
('Port Authority',        'Jacksonville',  'FL', 'USA', 32),
('Customs Office',        'Memphis',       'TN', 'USA', 33),
('Telecom Office',        'Louisville',    'KY', 'USA', 34),
('City Planning Dept',    'Richmond',      'VA', 'USA', 35),
('Welfare Office',        'Oklahoma City', 'OK', 'USA', 36),
('Airport Terminal',      'Tucson',        'AZ', 'USA', 37),
('Farm District',         'Fresno',        'CA', 'USA', 38),
('State Prison',          'Mesa',          'AZ', 'USA', 39),
('Defense Ministry',      'Washington',    'DC', 'USA', 40);

-- Notes
INSERT INTO Note (Content, Created_Date, Story_ID) VALUES
('Anonymous tip received.',            '2025-01-08', 1),
('Fraud confirmed by accountant.',     '2025-02-22', 2),
('Water samples collected.',           '2025-03-06', 3),
('Medical audit initiated.',           '2025-03-25', 4),
('Property seizure under review.',     '2025-04-10', 5),
('Grant audit in progress.',           '2025-04-15', 6),
('Witness came forward.',              '2025-01-22', 7),
('Fake drug batch identified.',        '2025-02-06', 8),
('Permit numbers cross-checked.',      '2025-02-24', 9),
('Fund transfer records obtained.',    '2025-03-09', 10),
('Lab analysis pending.',              '2025-03-23', 11),
('Loan documents flagged.',            '2025-04-08', 12),
('Ballot audit requested.',            '2025-01-13', 13),
('Contamination source identified.',   '2025-02-19', 14),
('Farmer testimonies collected.',      '2025-03-13', 15),
('Tax discrepancy confirmed.',         '2025-04-04', 16),
('Factory inspection scheduled.',      '2025-01-28', 17),
('Kickback payments traced.',          '2025-03-02', 18),
('Construction audit started.',        '2025-03-28', 19),
('IP addresses logged.',               '2025-04-18', 20),
('Seizure report filed.',              '2025-01-09', 21),
('Fund statements obtained.',          '2025-02-11', 22),
('Admission records requested.',       '2025-03-15', 23),
('Survey data collected.',             '2025-04-11', 24),
('Subsidy claims reviewed.',           '2025-01-21', 25),
('Aid distribution tracked.',          '2025-02-28', 26),
('Fine records obtained.',             '2025-03-21', 27),
('Device approval reviewed.',          '2025-04-15', 28),
('License docs reviewed.',             '2025-01-25', 29),
('Betting records obtained.',          '2025-02-21', 30),
('Financial statements reviewed.',     '2025-03-25', 31),
('Import clearance checked.',          '2025-04-21', 32),
('Customs records obtained.',          '2025-01-31', 33),
('License applications reviewed.',     '2025-02-25', 34),
('Planning permits checked.',          '2025-03-31', 35),
('Welfare claims reviewed.',           '2025-04-25', 36),
('Contract docs obtained.',            '2025-02-02', 37),
('Pesticide samples collected.',       '2025-03-01', 38),
('Activity logs reviewed.',            '2025-04-02', 39),
('Procurement files obtained.',        '2025-04-28', 40);

-- Timeline Events
INSERT INTO Timeline_Event (Event_Title, Event_Date, Description, Story_ID) VALUES
('Budget Approved',              '2024-06-01', 'City approved new allocation.',       1),
('Fraud Complaint Filed',        '2025-02-05', 'Legal complaint submitted.',          2),
('Waste Reported',               '2025-03-02', 'Residents reported pollution.',       3),
('Insurance Audit Start',        '2025-03-18', 'Internal audit initiated.',           4),
('Property Investigation Start', '2025-04-03', 'Financial tracking started.',         5),
('Grant Investigation Start',    '2025-04-12', 'Education department review.',        6),
('Bribery Complaint Filed',      '2025-01-16', 'First complaint received.',           7),
('Drug Recall Issued',           '2025-02-02', 'Batch recalled from hospitals.',      8),
('Mining Halt Ordered',          '2025-02-21', 'Operations suspended.',               9),
('Fund Freeze Initiated',        '2025-03-06', 'Accounts frozen pending review.',     10),
('Water Advisory Issued',        '2025-03-21', 'Public warned about water.',          11),
('Bank Audit Started',           '2025-04-06', 'Regulatory audit commenced.',         12),
('Recount Demanded',             '2025-01-11', 'Opposition demands recount.',         13),
('Food Ban Issued',              '2025-02-16', 'Affected food products banned.',      14),
('Court Order Filed',            '2025-03-11', 'Farmers file court case.',            15),
('Tax Raid Conducted',           '2025-04-02', 'IT department raids offices.',        16),
('Factory Sealed',               '2025-01-26', 'Labour dept seals factory.',          17),
('Doctor Suspended',             '2025-03-01', 'License suspended pending probe.',    18),
('Contractor Arrested',          '2025-03-26', 'Main contractor taken into custody.', 19),
('Accounts Frozen',              '2025-04-16', 'Suspect accounts frozen by bank.',    20),
('Arms Cache Found',             '2025-01-06', 'Weapons cache discovered.',           21),
('Pension Audit Started',        '2025-02-09', 'Financial review initiated.',         22),
('Admission Probe Started',      '2025-03-13', 'Investigation begins.',               23),
('Forest Survey Done',           '2025-04-09', 'Satellite survey completed.',         24),
('Subsidy Freeze Ordered',       '2025-01-19', 'Payments suspended.',                 25),
('Aid Audit Initiated',          '2025-02-26', 'Distribution review started.',        26),
('Traffic Division Probe',       '2025-03-19', 'Internal probe initiated.',           27),
('Device Recall Issued',         '2025-04-13', 'Devices recalled from hospitals.',    28),
('Mining License Suspended',     '2025-01-23', 'Operations halted.',                  29),
('Match Fixing Exposed',         '2025-02-19', 'Players come forward.',               30),
('NGO Audit Initiated',          '2025-03-23', 'Financial review started.',           31),
('Import Shipment Seized',       '2025-04-19', 'Contaminated goods seized.',          32),
('Customs Officer Suspended',    '2025-01-29', 'Officer under investigation.',        33),
('License Freeze Ordered',       '2025-02-23', 'New licenses suspended.',             34),
('Planning Dept Probe',          '2025-03-29', 'Investigation launched.',             35),
('Welfare Fraud Detected',       '2025-04-23', 'Ghost claimants identified.',         36),
('Airport Audit Started',        '2025-01-31', 'Contract review initiated.',          37),
('Crop Ban Issued',              '2025-02-27', 'Affected crops recalled.',            38),
('Prison Warden Suspended',      '2025-03-31', 'Warden under investigation.',         39),
('Procurement Freeze',           '2025-04-26', 'All procurement halted.',             40);

-- =====================================================
-- STEP 5: TRIGGERS
-- =====================================================
DELIMITER $$

CREATE TRIGGER trg_story_insert
AFTER INSERT ON Story
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (Table_Name, Operation, Record_ID, New_Value)
    VALUES ('Story', 'INSERT', NEW.Story_ID,
            CONCAT('Title=', NEW.Title, ' | Category=', NEW.Category, ' | Status=', NEW.Status));
END$$

CREATE TRIGGER trg_story_update
AFTER UPDATE ON Story
FOR EACH ROW
BEGIN
    IF OLD.Status <> NEW.Status THEN
        INSERT INTO Audit_Log (Table_Name, Operation, Record_ID, Old_Value, New_Value)
        VALUES ('Story', 'UPDATE', NEW.Story_ID,
                CONCAT('Status=', OLD.Status),
                CONCAT('Status=', NEW.Status));
    END IF;
END$$

CREATE TRIGGER trg_source_credibility_update
AFTER UPDATE ON Source
FOR EACH ROW
BEGIN
    IF OLD.Credibility_Level <> NEW.Credibility_Level THEN
        INSERT INTO Audit_Log (Table_Name, Operation, Record_ID, Old_Value, New_Value)
        VALUES ('Source', 'UPDATE', NEW.Source_ID,
                CONCAT('Credibility=', OLD.Credibility_Level),
                CONCAT('Credibility=', NEW.Credibility_Level));
    END IF;
END$$

CREATE TRIGGER trg_prevent_source_delete
BEFORE DELETE ON Source
FOR EACH ROW
BEGIN
    DECLARE linked_ongoing INT;
    SELECT COUNT(*) INTO linked_ongoing
    FROM Interview i
    JOIN Story s ON i.Story_ID = s.Story_ID
    WHERE i.Source_ID = OLD.Source_ID
      AND s.Status = 'Ongoing'
      AND OLD.Credibility_Level = 3;
    IF linked_ongoing > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete a High credibility source linked to an Ongoing story.';
    END IF;
END$$

CREATE TRIGGER trg_interview_insert
AFTER INSERT ON Interview
FOR EACH ROW
BEGIN
    INSERT INTO Audit_Log (Table_Name, Operation, Record_ID, New_Value)
    VALUES ('Interview', 'INSERT', NEW.Interview_ID,
            CONCAT('Story_ID=', NEW.Story_ID, ' | Source_ID=', NEW.Source_ID, ' | Mode=', NEW.Mode));
END$$

DELIMITER ;

-- =====================================================
-- STEP 6: STORED PROCEDURES
-- =====================================================
DELIMITER $$

CREATE PROCEDURE sp_transfer_interviews(
    IN p_from_source INT,
    IN p_to_source   INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'ERROR: Transfer rolled back. No changes made.' AS Result;
    END;
    START TRANSACTION;
        UPDATE Interview SET Source_ID = p_to_source WHERE Source_ID = p_from_source;
        INSERT INTO Audit_Log (Table_Name, Operation, Record_ID, Old_Value, New_Value)
        VALUES ('Interview', 'UPDATE', p_from_source,
                CONCAT('Source_ID=', p_from_source),
                CONCAT('Transferred to Source_ID=', p_to_source));
    COMMIT;
    SELECT CONCAT('Success: Interviews transferred from Source ', p_from_source,
                  ' to Source ', p_to_source) AS Result;
END$$

CREATE PROCEDURE sp_complete_story(
    IN p_story_id INT
)
BEGIN
    DECLARE v_current_status VARCHAR(50);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'ERROR: Story completion rolled back.' AS Result;
    END;
    SELECT Status INTO v_current_status FROM Story WHERE Story_ID = p_story_id;
    IF v_current_status = 'Completed' THEN
        SELECT 'Story is already Completed.' AS Result;
    ELSE
        START TRANSACTION;
            UPDATE Story SET Status = 'Completed' WHERE Story_ID = p_story_id;
            INSERT INTO Audit_Log (Table_Name, Operation, Record_ID, Old_Value, New_Value)
            VALUES ('Story', 'UPDATE', p_story_id, 'Status=Ongoing', 'Status=Completed');
        COMMIT;
        SELECT CONCAT('Story ID ', p_story_id, ' marked as Completed.') AS Result;
    END IF;
END$$

CREATE PROCEDURE sp_upgrade_credibility(
    IN p_source_id INT,
    IN p_new_level INT
)
BEGIN
    DECLARE v_old_level INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'ERROR: Credibility update rolled back.' AS Result;
    END;
    START TRANSACTION;
        SELECT Credibility_Level INTO v_old_level
        FROM Source WHERE Source_ID = p_source_id FOR UPDATE;
        IF p_new_level NOT IN (1,2,3) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid credibility level. Use 1, 2, or 3.';
        END IF;
        UPDATE Source SET Credibility_Level = p_new_level WHERE Source_ID = p_source_id;
        INSERT INTO Audit_Log (Table_Name, Operation, Record_ID, Old_Value, New_Value)
        VALUES ('Source', 'UPDATE', p_source_id,
                CONCAT('Credibility=', v_old_level),
                CONCAT('Credibility=', p_new_level));
    COMMIT;
    SELECT CONCAT('Source ', p_source_id, ' credibility updated from ',
                  v_old_level, ' to ', p_new_level) AS Result;
END$$

DELIMITER ;

-- =====================================================
-- STEP 7: VIEWS
-- =====================================================

CREATE OR REPLACE VIEW v_source_overview AS
SELECT s.Source_ID, s.Name, s.Type, s.Contact_Info,
    CASE s.Credibility_Level WHEN 1 THEN 'Low' WHEN 2 THEN 'Medium' WHEN 3 THEN 'High' END AS Credibility,
    COUNT(DISTINCT i.Interview_ID) AS Total_Interviews
FROM Source s LEFT JOIN Interview i ON s.Source_ID = i.Source_ID
GROUP BY s.Source_ID, s.Name, s.Type, s.Contact_Info, s.Credibility_Level;

CREATE OR REPLACE VIEW v_story_overview AS
SELECT st.Story_ID, st.Title, st.Category, st.Status, st.Start_Date,
    COUNT(DISTINCT i.Interview_ID) AS Total_Interviews,
    COUNT(DISTINCT d.Document_ID)  AS Total_Documents,
    COUNT(DISTINCT n.Note_ID)      AS Total_Notes,
    COUNT(DISTINCT te.Event_ID)    AS Total_Events,
    COUNT(DISTINCT l.Location_ID)  AS Total_Locations
FROM Story st
LEFT JOIN Interview i     ON st.Story_ID = i.Story_ID
LEFT JOIN Document d      ON st.Story_ID = d.Story_ID
LEFT JOIN Note n          ON st.Story_ID = n.Story_ID
LEFT JOIN Timeline_Event te ON st.Story_ID = te.Story_ID
LEFT JOIN Location l      ON st.Story_ID = l.Story_ID
GROUP BY st.Story_ID, st.Title, st.Category, st.Status, st.Start_Date;

CREATE OR REPLACE VIEW v_location_story AS
SELECT l.Location_ID, l.Place_Name, l.City, l.State, l.Country,
    st.Story_ID, st.Title AS Story_Title, st.Category, st.Status
FROM Location l JOIN Story st ON l.Story_ID = st.Story_ID;

CREATE OR REPLACE VIEW v_interview_details AS
SELECT i.Interview_ID, i.Interview_Date, i.Mode, i.Transcript,
    s.Name AS Source_Name, s.Type AS Source_Type,
    CASE s.Credibility_Level WHEN 1 THEN 'Low' WHEN 2 THEN 'Medium' WHEN 3 THEN 'High' END AS Credibility,
    st.Title AS Story_Title, st.Category, st.Status
FROM Interview i
JOIN Source s  ON i.Source_ID = s.Source_ID
JOIN Story st  ON i.Story_ID  = st.Story_ID;

CREATE OR REPLACE VIEW v_document_details AS
SELECT d.Document_ID, d.Title AS Document_Title, d.Type AS Document_Type, d.Upload_Date,
    st.Title AS Story_Title, st.Category, st.Status
FROM Document d JOIN Story st ON d.Story_ID = st.Story_ID;

CREATE OR REPLACE VIEW v_timeline_details AS
SELECT te.Event_ID, te.Event_Title, te.Event_Date, te.Description AS Event_Description,
    st.Title AS Story_Title, st.Category, st.Status
FROM Timeline_Event te JOIN Story st ON te.Story_ID = st.Story_ID;

CREATE OR REPLACE VIEW v_city_hotspot AS
SELECT l.City, l.State,
    COUNT(DISTINCT st.Story_ID)    AS Total_Stories,
    SUM(st.Status = 'Ongoing')     AS Ongoing_Stories,
    SUM(st.Status = 'Completed')   AS Completed_Stories,
    GROUP_CONCAT(DISTINCT st.Category ORDER BY st.Category) AS Categories
FROM Location l JOIN Story st ON l.Story_ID = st.Story_ID
GROUP BY l.City, l.State ORDER BY Total_Stories DESC;

CREATE OR REPLACE VIEW v_most_active_sources AS
SELECT s.Name, s.Type,
    CASE s.Credibility_Level WHEN 1 THEN 'Low' WHEN 2 THEN 'Medium' WHEN 3 THEN 'High' END AS Credibility,
    COUNT(DISTINCT i.Story_ID)    AS Stories_Involved,
    COUNT(DISTINCT i.Interview_ID) AS Total_Interviews,
    GROUP_CONCAT(DISTINCT st.Category ORDER BY st.Category) AS Story_Categories
FROM Source s
JOIN Interview i ON s.Source_ID = i.Source_ID
JOIN Story st    ON i.Story_ID  = st.Story_ID
GROUP BY s.Source_ID, s.Name, s.Type, s.Credibility_Level
ORDER BY Stories_Involved DESC;

CREATE OR REPLACE VIEW v_incomplete_stories AS
SELECT st.Story_ID, st.Title, st.Category, st.Status,
    COUNT(DISTINCT i.Interview_ID) AS Interviews,
    COUNT(DISTINCT d.Document_ID)  AS Documents,
    COUNT(DISTINCT n.Note_ID)      AS Notes,
    COUNT(DISTINCT te.Event_ID)    AS Timeline_Events,
    CASE
        WHEN COUNT(DISTINCT i.Interview_ID) = 0 THEN 'Missing Interviews'
        WHEN COUNT(DISTINCT d.Document_ID)  = 0 THEN 'Missing Documents'
        WHEN COUNT(DISTINCT te.Event_ID)    = 0 THEN 'Missing Timeline'
        ELSE 'Looks Complete'
    END AS Issue
FROM Story st
LEFT JOIN Interview i       ON st.Story_ID = i.Story_ID
LEFT JOIN Document d        ON st.Story_ID = d.Story_ID
LEFT JOIN Note n            ON st.Story_ID = n.Story_ID
LEFT JOIN Timeline_Event te ON st.Story_ID = te.Story_ID
GROUP BY st.Story_ID, st.Title, st.Category, st.Status;

CREATE OR REPLACE VIEW v_risky_source_story AS
SELECT st.Title AS Story_Title, st.Category, s.Name AS Source_Name,
    CASE s.Credibility_Level WHEN 1 THEN 'Low' WHEN 2 THEN 'Medium' WHEN 3 THEN 'High' END AS Credibility,
    i.Interview_Date, i.Mode
FROM Interview i
JOIN Source s  ON i.Source_ID = s.Source_ID
JOIN Story st  ON i.Story_ID  = st.Story_ID
WHERE s.Credibility_Level = 1
  AND st.Category IN ('Crime', 'Politics', 'Environment')
ORDER BY st.Category;

CREATE OR REPLACE VIEW v_user_roles AS
SELECT User_ID, Username, Role, Full_Name, Created_At FROM Users;

CREATE OR REPLACE VIEW v_audit_trail AS
SELECT Log_ID, Table_Name, Operation, Record_ID, Changed_By, Change_Time, Old_Value, New_Value
FROM Audit_Log ORDER BY Change_Time DESC;

-- =====================================================
-- STEP 8: SAMPLE QUERIES
-- =====================================================

-- Q1: All ongoing stories
SELECT Title, Category, Start_Date, Total_Interviews, Total_Documents
FROM v_story_overview WHERE Status = 'Ongoing';

-- Q2: All high credibility sources
SELECT Name, Type, Total_Interviews
FROM v_source_overview WHERE Credibility = 'High'
ORDER BY Total_Interviews DESC;

-- Q3: Stories by category (Crime)
SELECT Title, Status, Start_Date, Total_Interviews, Total_Documents
FROM v_story_overview WHERE Category = 'Crime';

-- Q4: Most active cities
SELECT City, State, Total_Stories, Ongoing_Stories, Categories
FROM v_city_hotspot LIMIT 10;

-- Q5: Documents for corruption stories
SELECT Document_Title, Document_Type, Upload_Date
FROM v_document_details WHERE Story_Title LIKE '%Corruption%';

-- Q6: Interviews for Reuters sources
SELECT Story_Title, Interview_Date, Mode, Transcript
FROM v_interview_details WHERE Source_Name LIKE '%Reuters%';

-- Q7: Recent timeline events
SELECT Event_Title, Event_Date, Event_Description, Story_Title
FROM v_timeline_details ORDER BY Event_Date DESC LIMIT 20;

-- Q8: Incomplete investigations
SELECT Title, Category, Issue
FROM v_incomplete_stories WHERE Issue != 'Looks Complete';

-- Q9: Sources in multiple story categories
SELECT Name, Type, Credibility, Stories_Involved, Story_Categories
FROM v_most_active_sources WHERE Stories_Involved > 2;

-- Q10: Low credibility sources in sensitive stories
SELECT Story_Title, Category, Source_Name, Credibility
FROM v_risky_source_story;

-- Q11: Full audit trail (Admin only)
SELECT Table_Name, Operation, Record_ID, Old_Value, New_Value, Change_Time
FROM v_audit_trail LIMIT 50;

-- Q12: Stories per category with status breakdown
SELECT Category, COUNT(*) AS Total_Stories,
       SUM(Status = 'Ongoing') AS Ongoing,
       SUM(Status = 'Completed') AS Completed
FROM Story GROUP BY Category ORDER BY Total_Stories DESC;

-- Q13: Unused sources (zero interviews)
SELECT s.Source_ID, s.Name, s.Type,
       CASE s.Credibility_Level WHEN 1 THEN 'Low' WHEN 2 THEN 'Medium' WHEN 3 THEN 'High' END AS Credibility
FROM Source s LEFT JOIN Interview i ON s.Source_ID = i.Source_ID
WHERE i.Interview_ID IS NULL;

-- Q14: Stories with most unique sources
SELECT st.Title, st.Category, COUNT(DISTINCT i.Source_ID) AS Unique_Sources
FROM Story st JOIN Interview i ON st.Story_ID = i.Story_ID
GROUP BY st.Story_ID, st.Title, st.Category
ORDER BY Unique_Sources DESC LIMIT 10;

-- Q15: Interview mode breakdown per story
SELECT st.Title,
       SUM(i.Mode = 'Online')    AS Online_Interviews,
       SUM(i.Mode = 'In-person') AS Inperson_Interviews
FROM Story st JOIN Interview i ON st.Story_ID = i.Story_ID
GROUP BY st.Story_ID, st.Title ORDER BY st.Title;

-- =====================================================
-- STEP 9: ACID DEMO CALLS
-- =====================================================

-- Demo 1: Mark a story as completed (Atomicity)
CALL sp_complete_story(1);

-- Demo 2: Safe credibility upgrade (Isolation)
CALL sp_upgrade_credibility(1, 2);

-- Demo 3: Transfer interviews between sources (Atomicity)
CALL sp_transfer_interviews(1, 2);

-- Demo 4: Check audit trail survived (Durability)
SELECT * FROM Audit_Log ORDER BY Change_Time DESC LIMIT 10;

-- Demo 5: Trigger verification — insert a story and check audit log
INSERT INTO Story (Title, Description, Category, Start_Date, Status)
VALUES ('Test Trigger Story', 'Verifying trigger fires.', 'Politics', CURDATE(), 'Ongoing');
SELECT * FROM Audit_Log WHERE Table_Name = 'Story' ORDER BY Change_Time DESC LIMIT 3;