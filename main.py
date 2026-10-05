#Talking Data Starter Code

#Part 2 Setting up the program
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)

movieData = pd.read_csv('./rotten_tomatoes_movies.csv')
favMovie = input("What is your favorite movie (before 2020)?: ")

favBoolList = movieData["movie_title"] == favMovie
favData = movieData.loc[favBoolList].iloc[0]
print("Your movie was released in:", favData["year"])
print("The critic rating is:", favData["critic_rating"])
print("The audience rating is:", favData["audience_rating"])
print("The genre(s) is/are:", favData["genres"])


print("\n\n")

choosenGenre = input("Which of the movie's genres would you like to analyze?")
genreBoolList = movieData["genres"].str.contains(choosenGenre)
genreMovieData = movieData.loc[genreBoolList]
numOfMovies = genreMovieData.shape[0]

print("There are " + str(numOfMovies) + " movies under the category " + choosenGenre + ".")

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
input("Press enter to see more information about how " + favMovie +
      " compares to other movies in this genre.")

#Part 5 Describe data
#find min
min = min(genreMovieData["audience_rating"])
print("The min audience rating of the data set is: " + str(min))
print(favMovie + " is rated " + (str(favData["audience_rating"]-min)) + " points higher than the lowest rated movie.")
print()

#find max
max = max(genreMovieData["audience_rating"])
print("The max audience rating of the data set is: " + str(max))
print(favMovie + " is rated " + (str(max-favData["audience_rating"])) + " points lower than the highest rated movie.")
print()

#find mean
mean = genreMovieData["audience_rating"].mean()
mean = round(mean, 1)
print("The mean audience rating of the data set is: " + str(mean))
if favData["audience_rating"] > mean:
    print(favMovie + " is rated " + str(round(favData["audience_rating"]-mean, 2)) +" higher the mean movie rating.")
elif mean > favData["audience_rating"]:
    print(favMovie + " is rated " + str(round(mean-favData["audience_rating"], 2)) + " lower the mean movie rating.")
else:
    print("The rating and mean are equal")
print()

#find median
median = genreMovieData["audience_rating"].median()
print("The median audience rating of the data set is: " + str(median))
if favData["audience_rating"] > median:
    print(favMovie + " is rated " + (str(favData["audience_rating"]-median)) +" higher the median movie rating.")
elif median > favData["audience_rating"]:
    print(favMovie + " is rated " + (str(median-favData["audience_rating"])) + " lower the median movie rating.")
else:
    print("The rating and median are equal")
print()

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
input("Press enter to see data visualizations.")

#Part 6 Create graphs
#Create histogram
plt.figure()
counts, bins, patches = plt.hist(
    genreMovieData["audience_rating"],
    bins=20,
    range=(0, 100)
)
#Adds labels and adjusts histogram
plt.grid(True)
plt.title("Audience Ratings of "+ choosenGenre + " Movies")
plt.xlabel("Audience Ratings")
plt.ylabel("Number of "+ choosenGenre + " Movies")

max_index = counts.argmax()
bin_start = bins[max_index]
bin_end = bins[max_index + 1]

#Prints interpretation of histogram
print("According to the histogram, most movies in this genre fall between a rating of " +
    str(int(bin_start))+ "–" + str(int(bin_end)))
print()

#Show histogram
plt.show()
input("Press enter to see the next data visualization.")

#Create scatterplot
plt.figure()
plt.scatter(data = genreMovieData, x = "audience_rating", y = "critic_rating")

#Adds labels and adjusts scatterplot
plt.grid(True)
plt.title("Audience Rating vs. Critic Rating")
plt.xlabel("Audience Rating")
plt.ylabel("Critic Rating")
plt.xlim(0, 100)
plt.ylim(0, 100)

corr = genreMovieData["audience_rating"].corr(
    genreMovieData["critic_rating"]
)
corr = round(corr, 2)
if corr > 0.3:
    relationship = "a positive"
elif corr < -0.3:
    relationship = "a negative"
else:
    relationship = "no"

#Prints interpretation of scatterplot
print("According to the scatter plot, there is " + relationship + " correlation between audience ratings and critic ratings (correlation = " + str(corr) + ").")
print()


#Show scatterplot
plt.show()

print("\nThank you for reading through my data analysis!")
