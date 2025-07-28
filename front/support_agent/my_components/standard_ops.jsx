import { Blockquote, Center, Box, ScrollArea, Accordion} from '@mantine/core';
import { IconLibrary, IconHelpCircle } from '@tabler/icons-react';

export function SOPs(props) {
  const icon = <IconLibrary />;
  return (
    // 1. The outer wrapper sets the maximum height.
      // This creates the boundary for our component.
      <Box className='limited-height-flex custom-font-body'>
  
        {/* 2. The inner container fills the wrapper and manages the layout.
            It now has a defined height to distribute to its children. */}
        <Blockquote  color="lime" icon={icon} mt="xl" className='fill-flex-column' >
          {/* 3. The scrollable area grows to fill the remaining space.
              Since its parent (Blockquote) has a defined height, scrolling now works. */}
          <ScrollArea style={{ flexGrow: 1 }}>
          <Center   bg="var(--mantine-color-gray-light)">
            <MyAccordion   sop_cats = {props.sop_cats} />
          </Center>
  
          </ScrollArea>
          </Blockquote>
      </Box>
    );
  }

  function MyAccordion(props){

    const icon = <IconHelpCircle />;

      const items = props.sop_cats.map((item) => (
        <Accordion.Item key={item.id} value={item.sopid}>
          <Accordion.Control icon={icon}>{item.sopid} - {item.title}</Accordion.Control>
          <Accordion.Panel style={{ whiteSpace: 'pre-line' }} ><p >{item.description}</p></Accordion.Panel>
        </Accordion.Item>
      ));
    
      return (
        <Accordion  w="90%" pt={20} pb={20} variant="separated" radius="lg" >
          {items}
        </Accordion>
      );
    
  }