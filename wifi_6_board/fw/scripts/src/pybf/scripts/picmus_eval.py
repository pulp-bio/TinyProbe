"""
   Copyright (C) 2021 ETH Zurich. All rights reserved.

   Author: Wolfgang Boettcher, ETH Zurich

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# Basic libraries
import matplotlib
#matplotlib.use('QT4Agg')
from matplotlib import colors, cm, pyplot as plt
from matplotlib.patches import Rectangle, Circle

from pybf.pybf.visualization import log_compress

import numpy as np

class PicmusEval:

    def __init__(self, 
                bf_image,
                bf_obj):

        self.image = bf_image
        self.pixel_coords = bf_obj._pixels_coords.reshape(2, bf_obj._image_res[1], bf_obj._image_res[0])

    def evaluate_FWHM(self, points, is_plot=True, plot_name="FWHM_eval", latex_args=None):      
        """
            Method to obtain the full width at half maximum in the x and z direction for a given set of points.
            points      - Array of points the FWHM is to be calculated on. Per point: [x, z, width, height].    
                          Width, and height specify the patch in which the global maximum is found and used as the
                          center for FWHM calculation
            is_plot     - If true, the plot is shown and saved unter plot_name
            plot_name   - Name of the plot
            latex_args  - If not none, list of parameters for LaTeX plotting of the image
        """

        if(is_plot is True):
            if latex_args is not None:
                from matplotlib import rc
                rc('font',**{'family':'serif'})
                rc('text', usetex=True)
                plt.rcParams.update(latex_args)
                plt.tight_layout()

            # Log-scale
            abs_image = log_compress(np.abs(self.image), 50)
            # Image
            fig, ax = plt.subplots()
            ax.imshow(abs_image, 
                        cmap=cm.gray, 
                        origin="lower")

            ax.set_xlabel("X, px")
            ax.set_ylabel("Z, px")
            ax.invert_yaxis()
        
        FWHM_el_x = []
        FWHM_el_y = []
        for i in range(0, points.shape[0]):
            fwhm_x,fwhm_y , plot = self._resolution_el(points[i])
            FWHM_el_x.append(fwhm_x)
            FWHM_el_y.append(fwhm_y)

            x1, y1 = plot[0], plot[1]
            ax.plot(x1, y1, color='green')
            x2, y2 = plot[2], plot[3]
            ax.plot(x2, y2, color='red')
        
        FWHM_el_x = np.asarray(FWHM_el_x)
        FWHM_el_y = np.asarray(FWHM_el_y)

        if(is_plot is True):
            if latex_args is None:
                plt.show()
                fig.savefig(plot_name + '.png')
            else:
                plt.show()
                fig.savefig(plot_name + '.pdf', bbox_inches='tight', dpi=600)
        
        return FWHM_el_x, FWHM_el_y




    def evaluate_circ_contrast(self, cirles, is_plot=True, plot_name="Constrast_cirC", latex_args=None):
        """
            Method to obtain the constrast to noise ratio on circular patches for a given set of points.
            circles     - Position of the circles to evaluate [x,z, outer_radius, inner_radius]
            is_plot     - If true, the plot is shown and saved unter plot_name
            plot_name   - Name of the plot
            latex_args  - If not none, list of parameters for LaTeX plotting of the image
        """

        if(is_plot is True):
            if latex_args is not None:
                from matplotlib import rc
                rc('font',**{'family':'serif'})
                rc('text', usetex=True)
                plt.rcParams.update(latex_args)

            # Log-scale
            abs_image = log_compress(np.abs(self.image), 50)
            # Image
            fig, ax = plt.subplots(1, 1)
            ax.imshow(abs_image, 
                        cmap=cm.gray, 
                        origin="lower")

            ax.set_xlabel("X, px")
            ax.set_ylabel("Z, px")
            ax.invert_yaxis()

        CNR_el = []
        for i in range(0, cirles.shape[0]):
            cnr, plot = self._evaluate_circ(cirles[i])
            CNR_el.append(cnr)

            if(is_plot is True):
                ax.add_patch(Circle((plot[1], plot[0]), plot[2],
                    edgecolor = 'red',
                    fill=False,
                    lw=2))

                ax.add_patch(Circle((plot[1], plot[0]), plot[3],
                    edgecolor = 'green',
                    fill=False,
                    lw=2))

        CNR_el = np.asarray(CNR_el)

        if(is_plot is True):
            if latex_args is None:
                plt.show()
                fig.savefig(plot_name + '.png')
            else:
                plt.show()
                fig.savefig(plot_name + '.pdf', bbox_inches='tight', dpi=600)

        return CNR_el

    def evaluate_rect_contrast(self, rectangles, is_plot=True, plot_name="Constrast_rect", latex_args=None):
        if(is_plot is True):
            if latex_args is not None:
                from matplotlib import rc
                rc('font',**{'family':'serif'})
                rc('text', usetex=True)
                plt.rcParams.update(latex_args)
                plt.tight_layout()

            # Log-scale
            abs_image = log_compress(np.abs(self.image), 50)
            # Image
            fig, ax = plt.subplots(1, 1)
            ax.imshow(abs_image, 
                        cmap=cm.gray, 
                        origin="lower")

            ax.set_xlabel("X, px")
            ax.set_ylabel("Z, px")
            ax.invert_yaxis()

        CNR_el = []
        for i in range(0, rectangles.shape[0]):
            cnr, plot = self._evaluate_rectangles(rectangles[i])
            CNR_el.append(cnr)

            if(is_plot is True):
                ax.add_patch(Rectangle((plot[0], pot[1]), plot[2], plot[3],
                    edgecolor = 'red',
                    fill=False,
                    lw=2))
                ax.add_patch(Rectangle((plot[4], pot[5]), plot[6], plot[7],
                    edgecolor = 'green',
                    fill=False,
                    lw=2))

        CNR_el = np.asarray(CNR_el)

        if(is_plot is True):
            if latex_args is None:
                plt.show()
                fig.savefig(plot_name + '.png')
            else:
                plt.show()
                fig.savefig(plot_name + '.pdf', bbox_inches='tight')

        return CNR_el
    

    def _evaluate_rectangles(self, rectangles):

        x1 = rectangles[0]
        x2 = rectangles[4]
        y1 = rectangles[1]
        y2 = rectangles[5]
        w1 = rectangles[2]
        w2 = rectangles[6]
        h1 = rectangles[3]
        h2 = rectangles[7]

        i_x1 = 0
        i_x2 = 0
        i_x1_end = 0
        i_x2_end = 0
        # Get relevant x indices
        for i in range(0, self.pixel_coords.shape[2]):
            x_max = np.max(self.pixel_coords[0,:,i])
            if (x_max < x1):
                i_x1 = i + 1
            if (x_max < x2):
                i_x2 = i + 1
            if (x_max < (x1+w1)):
                i_x1_end = i + 1
            if (x_max < (x2+w2)):
                i_x2_end = i + 1

        assert(i_x1 <= i_x2)
        assert(i_x1 <= i_x1_end)
        assert(i_x2 <= i_x2_end)

        # Get relevant y indices
        for i in range(0, self.pixel_coords.shape[1]):
            y_max = np.max(self.pixel_coords[1,i,:])
            if (y_max < y1):
                i_y1 = i + 1
            if (y_max < y2):
                i_y2 = i + 1
            if (y_max < (y1+h1)):
                i_y1_end = i + 1
            if (y_max < (y2+h2)):
                i_y2_end = i + 1

        assert(i_y1 <= i_y2)
        assert(i_y1 <= i_y1_end)
        assert(i_y2 <= i_y2_end)

        # Get the 2 disjunct areas for contrast evaluation
        inner_rect = self.image[i_y2:i_y2_end, i_x2:i_x2_end].flatten()

        outer_rect = self.image[i_y1:i_y1_end, i_x1:i_x2].flatten()
        outer_rect = np.append(outer_rect, self.image[i_y1:i_y1_end, i_x2_end:i_x1_end].flatten())
        outer_rect = np.append(outer_rect, self.image[i_y1:i_y2, i_x2:i_x2_end].flatten())
        outer_rect = np.append(outer_rect, self.image[i_y2_end:i_y1_end, i_x2:i_x2_end].flatten())

        outer_mean = np.mean(np.absolute(outer_rect))
        inner_mean = np.mean(np.absolute(inner_rect))
        outer_variance = np.var(np.absolute(outer_rect))
        inner_variance = np.var(np.absolute(inner_rect))

        CNR = 20 * np.log10((np.abs(outer_mean - inner_mean))/(0.5*np.sqrt(inner_variance + outer_variance)))

        return CNR, np.asarray([i_x1, i_y1, (i_x1_end-i_x1), (i_y1_end - i_y1), i_x2, i_y2, (i_x2_end-i_x2), (i_y2_end - i_y2)])

    def _evaluate_circ(self, circle):
        x = circle[0]
        y = circle[1]
        r1 = circle[2]
        r2 = circle[3]

        # Get circle values
        # Use (x - x0)^2 + (y-y0)^2 = r^2 (Circle equation)
        inner_values = []
        outer_values = []
        for x_i in range(0, self.pixel_coords.shape[2]):
            for y_i in range(0, self.pixel_coords.shape[1]):
                radius = np.sqrt((self.pixel_coords[0,y_i,x_i] - x)**2 + (self.pixel_coords[1,y_i,x_i] - y)**2)
                # Inner circle
                if (radius < r2):
                    inner_values.append(np.abs(self.image[y_i,x_i]))

                # Outer circle
                if (radius > r2 and radius < r1 ):
                    outer_values.append(np.abs(self.image[y_i,x_i]))
        inner_values = np.asarray(inner_values)
        outer_values = np.asarray(outer_values)

        #Evaluate
        outer_mean = np.mean(outer_values)
        inner_mean = np.mean(inner_values)
        outer_variance = np.var(outer_values)
        inner_variance = np.var(inner_values)

        CNR = 20 * np.log10((np.abs(outer_mean - inner_mean))/(0.5*np.sqrt(inner_variance + outer_variance)))

        # Get Circle coordinates
        # Note: This code is for visualisation and might be not the most accurate
        diff_matr_x = np.abs(self.pixel_coords[0,:,:] - x)
        diff_matr_y = np.abs(self.pixel_coords[1,:,:] - y)
        diff_matr = diff_matr_x + diff_matr_y

        center_coords = np.asarray(np.unravel_index(diff_matr.argmin(), diff_matr.shape, order='C'))
        pixel_width = np.abs(self.pixel_coords[0, center_coords[0], center_coords[1]] - self.pixel_coords[0, center_coords[0], center_coords[1]+1])
        radius_px1 = np.round(r1 / pixel_width)
        radius_px2 = np.round(r2 / pixel_width)

        return CNR, np.asarray([center_coords[0], center_coords[1], radius_px1, radius_px2]) 

    

    def _resolution_el(self, point):
        x = point[0]
        y = point[1]
        w = point[2]
        h = point[3]

        i_x = 0
        i_x_end = 0
        # Get relevant x indices
        for i in range(0, self.pixel_coords.shape[2]):
            x_max = np.max(self.pixel_coords[0,:,i])
            if (x_max < x):
                i_x = i + 1
            if (x_max < (x+w)):
                i_x_end = i + 1

        assert(i_x <= i_x_end)

        # Get relevant y indices
        for i in range(0, self.pixel_coords.shape[1]):
            y_max = np.max(self.pixel_coords[1,i,:])
            if (y_max < y):
                i_y = i + 1
            if (y_max < (y+h)):
                i_y_end = i + 1

        assert(i_y <= i_y_end)

        # Get local maximum
        img_snippet = np.abs(self.image[i_y:i_y_end, i_x:i_x_end])
        max_pos = np.asarray(np.unravel_index(img_snippet.argmax(), img_snippet.shape, order='C'))
        max_val = np.amax(np.abs(self.image[i_y:i_y_end, i_x:i_x_end]))
        max_pos[0] = max_pos[0] + i_y
        max_pos[1] = max_pos[1] + i_x

        # X Sweep up
        i = max_pos[1]    
        while (i < self.pixel_coords.shape[2]-1):
            i = i + 1
            x_upper_val = 0.25*np.abs(self.image[max_pos[0], i-1]) + 0.5*np.abs(self.image[max_pos[0], i]) + 0.25*np.abs(self.image[max_pos[0], i+1])
            if (x_upper_val < 0.5*max_val):
                x_upper_i = i
                break

        # X Sweep down
        i = max_pos[1]
        while (i > 1):
            i = i - 1
            x_lower_val = 0.25*np.abs(self.image[max_pos[0], i-1]) + 0.5*np.abs(self.image[max_pos[0], i]) + 0.25*np.abs(self.image[max_pos[0], i+1])
            if (x_lower_val < 0.5*max_val):
                x_lower_i = i
                break

        # Y Sweep up
        i = max_pos[0]
        while (i < self.pixel_coords.shape[1]-1):
            i = i + 1
            y_upper_val = 0.25*np.abs(self.image[i-1, max_pos[1]]) + 0.5*np.abs(self.image[i, max_pos[1]]) + 0.25*np.abs(self.image[i+1, max_pos[1]])
            if (y_upper_val < 0.5*max_val):
                y_upper_i = i
                break

        # Y Sweep down
        i = max_pos[0]
        while (i > 1):
            i = i - 1
            y_lower_val = 0.25*np.abs(self.image[i-1, max_pos[1]]) + 0.5*np.abs(self.image[i, max_pos[1]]) + 0.25*np.abs(self.image[i+1, max_pos[1]])
            if (y_lower_val < 0.5*max_val):
                y_lower_i = i
                break

        # Calculate FWHM
        # X axis
        x_upper = self.pixel_coords[0, max_pos[0], x_upper_i]
        x_lower = self.pixel_coords[0, max_pos[0], x_lower_i]
        x_FWHM = x_upper - x_lower

        # Y axis
        y_upper = self.pixel_coords[1, y_upper_i, max_pos[1]]
        y_lower = self.pixel_coords[1, y_lower_i, max_pos[1]]
        y_FWHM = y_upper - y_lower

        x1, y1 = [max_pos[1], max_pos[1]], [y_lower_i, y_upper_i]
        x2, y2 = [x_lower_i, x_upper_i], [max_pos[0], max_pos[0]]

        return x_FWHM, y_FWHM, np.asarray([x1, y1, x2, y2])