# horsing_around
Bet your horses his is going to work.

## Welcome to the money making scheme which will change your lyf!
jokes
### Project aims
Predict horse racing results = make money

### Project parts
#### Data
Currently have a data set from Kaggle in csv format.  (https://www.kaggle.com/lukebyrne/horses-for-courses).  Its large (222k horses) so best of downloading yourself, rather than clogging up the repo.  All data is on Aussie horse races
#####  Convert to SQL database
I think it would lend itself to it well as you can have race id, horse id, jockey id etc, to access data well, plus I want to learn SQL better.

The features in the data are extensive, may struggle to find that level of detail elsewhere, should think of ways we can create some of the featues.

#### Initial data exploration
Need to get a feel for the data, see if any trends can be spotted

#### Feature creation
May need to create some features.  Current ideas:

- Understanding how far behind the winner would be useful so margin would be a good feature in the data, however will create data leakage, so need to give the horses a "previous margin" stat.
- Need to classify the race type better I think.

#### Training models
Need to research what is a good idea

#### Test various betting strategies
Baselines - bet on the favourite according to the odds

Compare the odds offered for each case with the probability that the model spits out.  To find value.

#### Connect to Betfair API
So we can get upto data information and make

### Some horse racing lingo which will help understand the dataset
Margin - how far did the horse lose by (lengths) <br>
ground conditions / going -  THe code for these varies for different countries (https://en.wikipedia.org/wiki/Going_(horse_racing)) <br>
barrier -  This the the gate the horse starts in.
form_ratings - Not sure how these are caculated.
last_five_starts or last_twenty_starts - see guide (https://www.racingexplained.co.uk/picking-a-winner/reading-the-form/). An 'x' is a spell in this case (spell = 3 month break from racing)
field_strength - measures the difference between the quality of the field against which the horse raced last start and will confront in the forthcoming race. Bear in mind that races of exactly the same class can vary in strength. This means the level of competition the horse is meeting in a Welter Handicap tomorrow could be 1.5kg “tougher” than the Welter field it raced at its last start and so on. In the FS column +1.5 means tomorrow’s field is 1.5kg stronger than the horse met last start. On the other hand, -2.0 means tomorrow’s race is 2kg “weaker” than its last start, thereby making the task of the horse easier than might be expected given that it is racing in the “same” class. Falvelon has a Field Strength figure of +5.5 meaning that this race is a 5.5Kg stronger quality race than its last start race.
prize_money - total career earnings
break down of starts/places/wins -  track - is the venue itself (I thnk)
                                    firm/good/dead/slow/soft/heavy - are the going.  How to aussies defined the going changed                                                                      in 2014.  I propose we ignore dead and slow but should                                                                        double check.  These need to be standardised across                                                                          different countries though.
                                    distance - specific distance
                                    class_same - races in the same class as the race.  (races have classes, which probably                                                    differ between countries
                                    class_stronger - races in a stronger class?  (this is a guess)
                                    first_up - First race after a spell (3 month break from racing)
                                    second_up - First race after first_up race
                                    






