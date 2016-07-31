""" DBSCAN: Density-Based Spatial Clustering of
        Applications with Noise

Author: James Pan <jamesjpan@outlook.com>

Reference:
    Ester, M., H. P. Kriegel, J. Sander, and X. Xu, "A
        Density-Based Algorithm for Discovering Clusters
        in Large Spatial Databases with Noise". Proceedings
        of the 2nd International Conference on Knowledge
        Discovery and Data Mining, Portland, OR, AAAI
        Press, pp. 226 - 231. 1996
"""

class Cluster(object):
    """ A Cluster is just a wrapper for a list of points.
    Each Cluster object has a unique id. DBSCAN.run()
    returns a list of Clusters.
    """

    cid = 0 # Keep track of cluster ids

    def __init__(self):
        self.cid = Cluster.cid
        self.pts = []

        Cluster.cid += 1 # Increment the global id

    def addPoint(self, p):
        self.pts.append(p)


class DBSCAN(object):
    """ Parameters
        ----------

        D: list of tuples
            stores points as a list of tuples
            of the form (<string id>, <float x>, <float y>)

            E.g. D = [('001', 0.5, 2.1), ('002', 1.0, 2.4)]

            Point ids don't have to be unique.

        eps: float
            maximum distance for two points to be
            considered the same neighborhood

            E.g. 0.001

        minPts: int
            Minimum number of points in a neighborhood for
            a point to be considered a core point. This
            includes the point itself.

            E.g. 4


        Returns
        -------

        A tuple of a list of Cluster objects and a list of
        noise, e.i. ([<list clusters>, <list noise pts>])


        Methods
        -------

        printClusters() - handy method for printing results
        run()           - run DBSCAN

        Example Usage
        -------------

        import dbscan

        dbs = DBSCAN(D, 0.001, 4)
        clusters = dbs.scan()

        # Print with printClusters
        dbs.printClusters()

        # Print with iteration
        for cluster in clusters:
            print(cluster.cid, cluster.pts)

    """

    def __init__(self, D, eps, minPts):
        self.D = D
        self.minPts = minPts

        # This implementation uses Manhattan distance
        # so the eps is squared. This is because
        # calculating sqrt for Euclidean distance is much
        # slower than calculating squares.
        self.eps = eps*eps

        self.Clusters   = []    # Results stored here
        self.NOISE      = []    # Noise points
        self.visited    = []    # For keeping track of pts

    def __regionQuery(self, pt):
        eps = self.eps
        D = self.D

        # This implementation uses Manhattan distance
        # to avoid doing an expensive sqrt calculation.
        neighborhood = [
            p for p in D if (
                    (p[1] - pt[1])**2
                    + (p[2] - pt[2])**2 <= eps
                )
            ]
        return neighborhood

    def __expandCluster(self, pt, NeighborhoodPts, C):
        C.addPoint(pt)

        # Localize for some performance boost.
        visited                 = self.visited
        appendVisited           = visited.append
        regionQuery             = self.__regionQuery
        minPts                  = self.minPts
        appendNeighborhoodPts   = NeighborhoodPts.append
        Clusters                = self.Clusters

        for p in NeighborhoodPts:
            if p not in visited:
                appendVisited(p)
                NewNeighborhoodPts = regionQuery(p)
                if len(NewNeighborhoodPts) >= minPts:
                    for n in NewNeighborhoodPts:
                        if n not in NeighborhoodPts:
                            appendNeighborhoodPts(n)

            # Check if p in any clusters
            for cluster in Clusters:
                if p not in cluster.pts:
                    if p not in C.pts:
                        C.addPoint(p)
                        break

    def printClusters(self):
        for cluster in self.Clusters:
            cid = cluster.cid
            pts = cluster.pts
            print("Cluster %d" % cid)
            for p in pts:
                print(
                    "id = %s x = %f y = %f"
                    % (p[0], p[1], p[2])
                )

    def run(self):
        for pt in self.D:
            if pt not in self.visited:
                self.visited.append(pt)
                NeighborhoodPts = self.__regionQuery(pt)
                if len(NeighborhoodPts) < self.minPts:
                    self.NOISE.append(pt)
                else:
                    C = Cluster() # new cluster
                    self.Clusters.append(C)
                    self.__expandCluster(
                            pt, NeighborhoodPts, C
                        )

        return (self.Clusters, self.NOISE)


# Test
def test(csv):
    D = []
    pt = ()

    lines = open(csv, 'r').read().splitlines()

    # If using the sample iris.data included in the
    # repository, each line is structured:
    #
    # <float sl>, <float sw>, <float pl>, <float pw>, <string id>
    #
    # For sepal length vs petal length comparison, use:
    #
    # pt = (cols[4], float(cols[2]), float(cols[0])
    #
    # Check for more information:
    # https://en.wikipedia.org/wiki/Iris_flower_data_set
    for line in lines:
        cols = line.split(',')
        pt = (cols[4], float(cols[2]), float(cols[0]))
        D.append(pt)

    # Remember to set a value for eps and minPts. Here
    # they are set to 0.3 and 3.
    myDBSCAN = DBSCAN(D, 0.3, 3)

    results = myDBSCAN.run()
    clusters = results[0]
    noise = results[1]

    # Teting printClusters()
    myDBSCAN.printClusters()

    # Manually printing
    for cluster in clusters:
        print(cluster.cid, cluster.pts)

    # Plotting the results
    import matplotlib.pyplot as plt
    for cluster in clusters:
        x = []
        y = []
        for pt in cluster.pts:
            x.append(pt[1])
            y.append(pt[2])
        plt.plot(x, y, '.')

    noise_x = []
    noise_y = []
    for pt in noise:
        noise_x.append(pt[1])
        noise_y.append(pt[2])
    plt.plot(noise_x, noise_y, 'x')

    plt.axis("equal")
    plt.xlim(xmin=0.0)
    plt.ylim(ymin=4.0)
    plt.xlabel("Petal Length")
    plt.ylabel("Sepal Length")
    plt.show()

