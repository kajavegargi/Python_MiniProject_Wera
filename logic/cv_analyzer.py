import cv2
import numpy as np

def analyze_stains(image):
    """
    Stain detection works by converting the image into the LAB color space,
    blurring the color channels to find a uniform version, and comparing.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    # Blur to create the "uniform" version
    blurred = cv2.GaussianBlur(lab, (51, 51), 0)
    
    # Get color channels a and b
    a_diff = cv2.absdiff(lab[:,:,1], blurred[:,:,1])
    b_diff = cv2.absdiff(lab[:,:,2], blurred[:,:,2])
    
    color_diff = cv2.add(a_diff, b_diff)
    
    # Threshold to find sharp divergences
    _, anomaly_map = cv2.threshold(color_diff, 30, 255, cv2.THRESH_BINARY)
    
    stain_ratio = np.sum(anomaly_map > 0) / anomaly_map.size
    
    if stain_ratio > 0.05:
        risk = "High risk"
    elif stain_ratio > 0.02:
        risk = "Medium risk"
    else:
        risk = "Low risk"
        
    return anomaly_map, stain_ratio, risk

def analyze_tears(image):
    """
    Tear/hole detection uses Canny edge detection.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Blur slightly to remove noise
    blurred_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    edge_map = cv2.Canny(blurred_gray, 50, 150)
    
    edge_density = np.sum(edge_map > 0) / edge_map.size
    
    # Thresholds for edges (fabric has some natural edges, tears create more)
    if edge_density > 0.08:
        risk = "High risk"
    elif edge_density > 0.04:
        risk = "Medium risk"
    else:
        risk = "Low risk"
        
    return edge_map, edge_density, risk

def analyze_wrinkles(image):
    """
    Wrinkle scoring uses the Laplacian operator to measure pixel brightness variance.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    
    # Visualization map (absolute values mapped to 0-255)
    variance_map = cv2.convertScaleAbs(laplacian)
    
    # Smooth a bit for visual map
    # variance_map = cv2.applyColorMap(variance_map, cv2.COLORMAP_JET)
    
    if variance > 1000:
        risk = "High risk"
    elif variance > 400:
        risk = "Medium risk"
    else:
        risk = "Low risk"
        
    return variance_map, variance, risk

def calculate_final_grade(stain_risk, tear_risk, wrinkle_risk):
    risk_scores = {"High risk": 0, "Medium risk": 1, "Low risk": 2}
    
    total = risk_scores[stain_risk] + risk_scores[tear_risk] + risk_scores[wrinkle_risk]
    
    # Total max is 6.
    if total == 6:
        grade = "A (Like New)"
        condition = "Like New"
    elif total >= 4:
        grade = "B (Good)"
        condition = "Good"
    elif total >= 2:
        grade = "C (Fair)"
        condition = "Fair"
    else:
        grade = "D (Poor)"
        condition = "Poor"
        
    return grade, condition
