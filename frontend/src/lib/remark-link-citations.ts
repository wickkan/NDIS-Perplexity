import { visit, SKIP } from 'unist-util-visit';
import type { Plugin } from 'unified';
import type { Text, Root, PhrasingContent, Parent as MdastParent } from 'mdast';

/**
 * A remark plugin to transform inline numerical citations like [1], [2]
 * into markdown links that point to anchors like #ref-1, #ref-2.
 * It tries to avoid double-linking if a citation is already part of a link.
 */
const remarkLinkCitations: Plugin<[], Root> = () => {
  return (tree: Root) => {
    visit(tree, 'text', (node: Text, index: number | undefined, parent: MdastParent | null | undefined) => {
      // Ensure parent exists, has children, index is a number, and parent.children is an array
      if (!parent || !('children' in parent) || typeof index !== 'number' || !Array.isArray(parent.children)) {
        return; // Cannot operate, so skip
      }

      // If the parent is already a link, don't process this text node.
      if (parent.type === 'link') {
        return SKIP; // Tell visit to skip processing children of this link node
      }

      const originalValue = node.value;
      const createdNodes: PhrasingContent[] = [];
      let lastIndex = 0;
      const regex = /\[(\d+)\]/g; // Matches [1], [23], etc.
      let match;

      while ((match = regex.exec(originalValue)) !== null) {
        const citationNumber = match[1]; // The number, e.g., "1"
        const fullMatchText = match[0]; // The full match, e.g., "[1]"
        const matchStartIndex = match.index;

        // Add text segment before the current match
        if (matchStartIndex > lastIndex) {
          createdNodes.push({ type: 'text', value: originalValue.slice(lastIndex, matchStartIndex) });
        }

        // Create and add the link node for the citation
        createdNodes.push({
          type: 'link',
          url: `#ref-${citationNumber}`,
          children: [{ type: 'text', value: fullMatchText }],
        });

        lastIndex = regex.lastIndex;
      }

      // If no citations were found in this text node, do nothing.
      if (createdNodes.length === 0) {
        return;
      }

      // Add any remaining text segment after the last match
      if (lastIndex < originalValue.length) {
        createdNodes.push({ type: 'text', value: originalValue.slice(lastIndex) });
      }
      
      // Replace the original text node with the new array of text and link nodes.
      // The `parent.children` array can accept PhrasingContent items because the original
      // `node` (a Text node) is itself PhrasingContent.
      parent.children.splice(index, 1, ...createdNodes);
      
      // Adjust the index for the `visit` utility because we replaced 1 node 
      // with `createdNodes.length` nodes. This tells `visit` to continue processing
      // from the correct position after the newly inserted nodes.
      return index + createdNodes.length; 
    });
  };
};

export default remarkLinkCitations;
