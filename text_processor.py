import MeCab
from typing import List, Dict

class TextProcessor:
    def __init__(self):
        """初始化 MeCab"""
        self.mecab = MeCab.Tagger()
        self.max_chars_per_line = 35  # 增加字符限制
    
    def _split_long_sentence(self, sentence):
        """使用 MeCab 进行更智能的长句分割"""
        # 如果是引号内的对话，使用特殊处理
        if sentence.startswith('「') or sentence.startswith('『'):
            return self._split_dialog(sentence)
            
        # 使用 MeCab 进行详细分析
        nodes = []
        node = self.mecab.parseToNode(sentence)
        
        # 定义标点符号集合
        punctuation_marks = {
            "。", "！", "？", "、", "，", "」", "』", ")", "）", "}", "】", "』", "〕",
            ".", "!", "?", ",", ")", "}", "]"
        }
        
        # 收集所有节点
        while node:
            if node.surface:
                nodes.append({
                    'surface': node.surface,
                    'pos': node.feature.split(',')[0],
                    'feature': node.feature
                })
            node = node.next
        
        # 预处理：找出所有可能的分割点
        split_points = []
        current_length = 0
        for i, node in enumerate(nodes):
            surface = node['surface']
            current_length += len(surface)
            
            # 如果不是标点符号，且在合适的位置
            if (surface not in punctuation_marks and 
                current_length >= self.max_chars_per_line * 0.7 and
                current_length <= self.max_chars_per_line):
                
                # 检查是否是合适的分割词
                if (node['pos'] == "助詞" and surface in ["は", "が", "を", "に", "へ", "で", "から"] or
                    node['pos'] == "接続助詞" and surface in ["て", "で"]):
                    
                    # 检查后面是否紧跟标点符号
                    next_node = nodes[i + 1] if i + 1 < len(nodes) else None
                    if not next_node or next_node['surface'] not in punctuation_marks:
                        split_points.append(i)
        
        # 如果没有找到合适的分割点，返回原句
        if not split_points and len(sentence) <= self.max_chars_per_line * 1.3:
            return [sentence]
        
        # 根据分割点分句
        parts = []
        current = []
        current_length = 0
        last_split = 0
        
        for i, node in enumerate(nodes):
            surface = node['surface']
            next_length = current_length + len(surface)
            
            # 如果当前是标点符号，总是加到当前行
            if surface in punctuation_marks:
                if current:
                    current.append(surface)
                    current_length += len(surface)
                elif parts:
                    parts[-1] += surface
                continue
            
            # 检查是否需要在这里分行
            if i in split_points:
                current.append(surface)
                parts.append(''.join(current))
                current = []
                current_length = 0
                last_split = i
            else:
                # 如果距离上次分割太远，强制分割
                if current_length > self.max_chars_per_line and i > last_split:
                    if current:
                        parts.append(''.join(current))
                        current = [surface]
                        current_length = len(surface)
                        last_split = i
                else:
                    current.append(surface)
                    current_length += len(surface)
        
        # 处理剩余部分
        if current:
            last_part = ''.join(current)
            if parts and len(parts[-1] + last_part) <= self.max_chars_per_line:
                parts[-1] += last_part
            else:
                parts.append(last_part)
        
        return parts or [sentence]

    def _split_dialog(self, text):
        """特别处理对话文本"""
        # 找到对话的开始和结束
        dialog_end = text.find('」') if '」' in text else text.find('』')
        if dialog_end == -1:
            return [text]
            
        dialog = text[:dialog_end+1]
        rest = text[dialog_end+1:].strip()
        
        result = []
        # 只有在对话特别长时才分割（增加容忍度）
        if len(dialog) <= self.max_chars_per_line * 1.5:  # 增加到1.5倍
            result.append(dialog)
        else:
            # 保留开始的引号
            quote = dialog[0]
            inner_text = dialog[1:-1]
            
            # 在标点符号处分割
            parts = []
            current = quote
            for char in inner_text:
                current += char
                # 只在句子真的很长时才分割
                if (char in ["、", "，", "！", "？", "。"] and 
                    len(current) >= self.max_chars_per_line * 1.2):
                    parts.append(current)
                    current = ""
            
            # 处理最后一部分
            if current:
                current += "」"
                parts.append(current)
            
            result.extend(parts)
        
        # 处理对话后的内容
        if rest:
            # 如果剩余部分不是很长，就和对话放在一起
            if len(rest) <= self.max_chars_per_line * 0.3:  # 添加这个判断
                result[-1] += rest
            else:
                if len(rest) > self.max_chars_per_line:
                    result.extend(self._split_long_sentence(rest))
                else:
                    result.append(rest)
        
        return result

    def _fix_quote_position(self, text):
        """修复引号位置，确保在句子末尾"""
        # 处理开头的引号
        if text.startswith('」'):
            text = text[1:] + '」'
        if text.startswith('』'):
            text = text[1:] + '』'
        
        return text

    def process_japanese_text(self, text):
        """使用 MeCab 处理日语文本"""
        # 首先用 MeCab 进行分词
        parsed = self.mecab.parse(text)
        sentences = []
        current = ""
        quote_stack = []  # 用于追踪引号
        
        # 处理 MeCab 的输出
        for line in parsed.split('\n'):
            if line == 'EOS' or line == '':
                continue
                
            # 分割为表层形式和特征
            surface = line.split('\t')[0]
            features = line.split('\t')[1].split(',')
            
            # 处理引号
            if surface in ['「', '『']:
                quote_stack.append(surface)
            elif surface in ['」', '』']:
                if quote_stack:  # 如果有对应的开引号
                    quote_stack.pop()
                else:  # 如果是孤立的闭引号，先不添加
                    continue
            
            # 添加当前词
            current += surface
            
            # 检查是否是句子结束
            if (surface in ["。", "！", "？", ".", "!", "?"] or  # 句号等
                (features[0] == "記号" and features[1] == "句点")):  # 句点标记
                
                # 处理未闭合的引号
                while quote_stack:
                    current += '」' if quote_stack.pop() == '「' else '』'
                
                if current.strip():
                    # 修复引号位置
                    current = self._fix_quote_position(current.strip())
                    
                    # 如果当前句子太长，进行分割
                    if len(current) > self.max_chars_per_line:
                        parts = self._split_long_sentence(current)
                        sentences.extend(parts)
                    else:
                        sentences.append(current)
                current = ""
                quote_stack = []  # 重置引号栈
                
        # 处理最后一个句子
        if current.strip():
            # 处理未闭合的引号
            while quote_stack:
                current += '」' if quote_stack.pop() == '「' else '』'
            
            # 修复引号位置
            current = self._fix_quote_position(current.strip())
            
            if len(current) > self.max_chars_per_line:
                parts = self._split_long_sentence(current)
                sentences.extend(parts)
            else:
                sentences.append(current)
                
        return sentences 

    def process_text_with_speakers(self, text_info: List[Dict]) -> List[Dict]:
        """处理带说话者信息的文本"""
        processed_sentences = []
        
        for sentence in text_info:
            text = sentence["text"]
            speaker = sentence["speaker"]
            
            # 如果文本太长，进行分割
            if len(text) > self.max_chars_per_line:
                parts = self._split_long_sentence(text)
                for part in parts:
                    processed_sentences.append({
                        "text": part,
                        "speaker": speaker,
                        "type": sentence["type"]
                    })
            else:
                processed_sentences.append(sentence)
        
        return processed_sentences 