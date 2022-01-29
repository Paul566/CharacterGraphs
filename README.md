Take a book. Count the number of pages where the two given characters are mentioned together. This is a measure of how strong the characters have interacted throughout the book. Then draw a graph of the characters in a book with the weights of edges being proportional to the strengths of interactions. Here are a few examples. More can be found in the `figures` repository.

![](figures/LTR3.png)
![](figures/SIF4.png)
![](figures/HP2.png)
![](figures/WP.png)
![](figures/MM.png)

Now define a distance between two characters as sqrt((d<sub>1</sub> + 1)(d<sub>2</sub> + 1)) / (w<sub>12</sub> + 1), where w<sub>12</sub> is the weight of the edge, d_1 and d_2 are sums of weights of all the edges outgoing from the first and the second vertex respectively. We need "+1" in the denominator in order not to divide by zero occasionally if the two characters have never interacted. We need "+1"s in the numerator to avoid placing the character who is not present in the book at zero distance from everybody else. <br />
It is worth noting that this "distance" does not obey the triangle inequality (a triangle with weights of edges 1, 5, 5 is a counterexample), and hence is not a valid metric. <br />
Now take a positive *r*. If the distance between some two characters is not greater than *r*, draw an edge between them. If some three characters have pairwise distances between them not greater than *r*, draw a face containing them. Generally, if all pairwise distances between *k+1* characters are not greater than *r*, let them form a *k*-dimensional simplex. We will get a simplicial complex, known as the Vietoris-Rips complex. When a healthy person encounters a simplicial complex, he experiences an irresistible desire to compute its' homologies. So let's increase *r* from zero to infinity, track the times of birth and death of cycles, and plot them.
