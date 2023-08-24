
from osgeo import ogr
import math,sys

class MWVD():
    def ApoloniusCircle(self, s1, s2, weight1, weight2, extent): #ogrpoint s1,s2, double weight1,weight2
        #Aurenhammer's formulae
        s1x = s1.GetX()
        s1y = s1.GetY()
        s2x = s2.GetX()
        s2y = s2.GetY()
        if(weight1 == weight2): #regular voronoi
            midpoint_x = (s1x+s2x)/2.
            midpoint_y = (s1y+s2y)/2.
            distance_x = s1x-s2x
            distance_y = s1y-s2y
            d = extent.GetBoundary().Length()
            #Create line features
            line = ogr.Geometry(ogr.wkbLineString)
            
            if (distance_y!=0):
                angle = math.atan(-1.*(distance_x/distance_y))
                line.AddPoint_2D(-d*math.cos(angle)+midpoint_x, -d*math.sin(angle)+midpoint_y)
                line.AddPoint_2D(d*math.cos(angle)+midpoint_x, d*math.sin(angle)+midpoint_y)
            else:
                line.AddPoint_2D(midpoint_x, -d+midpoint_y)
                line.AddPoint_2D(midpoint_x, d+midpoint_y)
            b = extent.GetBoundary()
            shortLine = line.Intersection(extent)
            diff = b.Difference(line)
            boundary = diff.GetGeometryRef(1)
            endPoint = boundary.GetPoint(0)
            boundary.AddPoint_2D(endPoint[0], endPoint[1])
            ring = ogr.Geometry(ogr.wkbLinearRing)
            for point in boundary.GetPoints():
                ring.AddPoint_2D(point[0], point[1])
            ring.AddGeometry(boundary)
            polygon = ogr.Geometry(ogr.wkbPolygon)
            polygon.AddGeometry(ring)
            
        else: #weighted voronoi
            den = 1./(weight1*weight1 - weight2*weight2)
            cx = (weight1*weight1*s2x - weight2*weight2*s1x)*den
            cy = (weight1*weight1*s2y - weight2*weight2*s1y)*den
            print('Center:', cx, cy)
            distance = math.sqrt(((s1x-s2x)*(s1x-s2x) + (s1y-s2y)*(s1y-s2y)))
            radius = weight1 * weight2 * distance * den
            print('Radius:', radius)
            if(radius<0):radius = radius*-1
            #creating the circle boundary from 3 points
            arc = ogr.Geometry(ogr.wkbCircularString)
            arc.AddPoint_2D(cx+radius, cy)
            arc.AddPoint_2D(cx-radius, cy)
            arc.AddPoint_2D(cx+radius, cy)
            #creating the circle polygon
            polygon = ogr.Geometry(ogr.wkbCurvePolygon)
            polygon.AddGeometry(arc)
        if s1.Intersects(polygon):
            return polygon
        else:
            return extent.Difference(polygon)

    def getMWVLayer(self, sites, outDS, layerName, extent):
        outLayer = outDS.CreateLayer(layerName, geom_type=ogr.wkbPolygon)
        for site1 in sites:
            dominance = extent
            for site2 in sites:
                if site1 != site2:
                    twoSitesDominance = self.ApoloniusCircle(site1['p'], site2['p'], site1['w'], site2['w'], extent)
                    dominance=dominance.Intersection(twoSitesDominance)
            # Get the output Layer's Feature Definition
            featureDefn = outLayer.GetLayerDefn()
            # create a new feature
            outFeature = ogr.Feature(featureDefn)
            # Set new geometry
            outFeature.SetGeometry(dominance.GetLinearGeometry())
            # Add new feature to output Layer
            outLayer.CreateFeature(outFeature)
            
    def readSitesFromLayer(self, ds, layerName, weightAttribute):
        layer = ds.GetLayerByName(layerName)
        sites = []
        for feature in layer:
            w = feature.GetFieldAsDouble(weightAttribute)
            p = feature.GetGeometryRef()
            sites.append({'p': p.Clone(),  'w': w})
        return sites
    # Create a line ring lring object, then add points to it one by one
    def getLayerExtent(self, ds, layerName):
        layer = ds.GetLayerByName(layerName)
        extent = ogr.Geometry(ogr.wkbPolygon)
        lring = ogr.Geometry(ogr.wkbLinearRing)
        le = layer.GetExtent()
        #add point
        lring.AddPoint(le[0], le[0])
        lring.AddPoint(le[0], le[3])
        lring.AddPoint(le[1], le[3])
        lring.AddPoint(le[1], le[0])
        lring.AddPoint(le[0], le[0])
        extent.AddGeometry(lring)
        # abs()取绝对值
        distance_abs = abs(le[0]-le[2])*2
        extent = extent.Buffer(distance_abs/10., 0)
        return extent

        

if __name__=="__main__":

    if (len(sys.argv)!=5):
        print("USAGE:")
        print("python pymwv.py ogrDataSource SitesLayerName WeightAttribute OutpuLayerName")
    else:
        runObj = MWVD()
        outDS = ogr.Open(sys.argv[1], 1)
        sites = runObj.readSitesFromLayer(outDS, sys.argv[2], sys.argv[3])
        extent = runObj.getLayerExtent(outDS, sys.argv[2])
        runObj.getMWVLayer(sites, outDS, sys.argv[4], extent)
 

