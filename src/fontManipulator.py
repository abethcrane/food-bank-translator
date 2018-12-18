import sys
from PIL import ImageFont

class FontManipulator():
    @staticmethod
    def get_font_with_offset(font, text):
        return map(sum, zip(font.getsize(text), font.getoffset(text)))

    @staticmethod
    def find_font_size_to_fit_height(lines, height, fontLocation, maxSize, lineSpacingHeight):
        # If we have to fit 5 lines in 2000 pixels then we have to fit 1 line in 400, so let's just calculate the max size to do that
        height /= len(lines)

        minfontsize = maxSize
        for line in lines:
            linesize = FontManipulator.find_font_size_to_fit(line, height - lineSpacingHeight, fontLocation, maxSize, False)
            if linesize < minfontsize:
                minfontsize = linesize

        return minfontsize

    @staticmethod
    def find_font_size_to_fit_width(text, width, fontLocation, maxSize):
        return FontManipulator.find_font_size_to_fit(text, width, fontLocation, maxSize, True)

    @staticmethod
    def find_font_size_to_fit(text, fit_value, fontLocation, maxSize, isWidth):
        # Maybe it's already perfect
        font = ImageFont.truetype(fontLocation, maxSize)
        w, h = FontManipulator.get_font_with_offset(font, text)
        if (isWidth):
            result = w
        else:
            result = h

        if (result < fit_value):
            return maxSize

        # If not, we do a binary search
        size = maxSize
        upperBound = maxSize
        lowerBound = 0
        upperBoundResult = result

        while True:
            font = ImageFont.truetype(fontLocation, size)
            w, h = FontManipulator.get_font_with_offset(font, text)
            if (isWidth):
                result = w
            else:
                result = h
            # If we find the perfect match, return it
            if result == fit_value:
                return size
            # If we blew over the top (say it was 74, and we tried a font size 49 and got 73, and font size 50 and got 75, we'd return the 73)
            elif result > upperBoundResult:
                return lowerBound
            # Business as usual - we have width 74, we got width 50, let's try a bigger font
            elif result > fit_value:
                upperBound = size
                upperBoundResult = result
            # Business as usual - we have width 74, we got width 100, so let's try a smaller font
            else:
                lowerBound = size
            prevsize = size
            size = lowerBound + ((upperBound - lowerBound) / 2)
            size = int(size)
            # Don't want to get caught inf looping
            if size == prevsize:
                return lowerBound

    @staticmethod    
    # Calculates the total text height for a list of words
    def calculate_total_text_height(list, width, fontLocation, idealFontSize, lineSpacingHeight):
        totalH = 0
        for line in list:
            fontSize = FontManipulator.find_font_size_to_fit_width(line, width, fontLocation, idealFontSize)
            font = ImageFont.truetype(fontLocation, fontSize)
            _, h = FontManipulator.get_font_with_offset(font, line)
            totalH += h + lineSpacingHeight
        return totalH - lineSpacingHeight # we don't need line spacing after the final word
        